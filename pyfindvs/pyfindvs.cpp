#include <Windows.h>
#include <Strsafe.h>
#include <Setup.Configuration.h>
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "oleaut32.lib")
#pragma comment(lib, "version.lib")
#pragma comment(lib, "Microsoft.VisualStudio.Setup.Configuration.Native.lib")

#include <Python.h>

PyObject *error_from_hr(HRESULT hr)
{
    if (FAILED(hr))
        PyErr_Format(PyExc_OSError, "Error %08x", hr);
    assert(PyErr_Occurred());
    return nullptr;
}

#define MAKE_STRING_GETTER(NAME, INTF, FUNC) \
    PyObject *NAME(INTF *inst) { \
        HRESULT hr; \
        BSTR bstr; \
        PyObject *str = nullptr; \
        if (FAILED(hr = inst-> FUNC (&bstr))) \
            return error_from_hr(hr); \
        str = PyUnicode_FromWideChar(bstr, SysStringLen(bstr)); \
        SysFreeString(bstr); \
        return str; \
    }

MAKE_STRING_GETTER(get_instance_id, ISetupInstance2, GetInstanceId);
MAKE_STRING_GETTER(get_install_version, ISetupInstance, GetInstallationVersion);
MAKE_STRING_GETTER(get_install_path, ISetupInstance, GetInstallationPath);
MAKE_STRING_GETTER(get_engine_path, ISetupInstance2, GetEnginePath);

PyObject *get_install_name(ISetupInstance2 *inst)
{
    HRESULT hr;
    BSTR name;
    PyObject *str = nullptr;
    if (FAILED(hr = inst->GetDisplayName(LOCALE_USER_DEFAULT, &name)))
        return error_from_hr(hr);
    str = PyUnicode_FromWideChar(name, SysStringLen(name));
    SysFreeString(name);
    return str;
}

MAKE_STRING_GETTER(get_package_id, ISetupPackageReference, GetId);
MAKE_STRING_GETTER(get_package_version, ISetupPackageReference, GetVersion);
MAKE_STRING_GETTER(get_package_type, ISetupPackageReference, GetType);

PyObject *get_installed_packages(ISetupInstance2 *inst)
{
    HRESULT hr;
    PyObject *res = nullptr;
    LPSAFEARRAY sa_packages = nullptr;
    LONG ub = 0;
    IUnknown **packages = nullptr;
    PyObject *str = nullptr;

    if (FAILED(hr = inst->GetPackages(&sa_packages)) ||
        FAILED(hr = SafeArrayAccessData(sa_packages, (void**)&packages)) ||
        FAILED(SafeArrayGetUBound(sa_packages, 1, &ub)) ||
        !(res = PyList_New(0)))
        goto error;

    for (LONG i = 0; i < ub; ++i) {
        ISetupPackageReference *package = nullptr;
        PyObject *id = nullptr;
        PyObject *version = nullptr;
        PyObject *type = nullptr;

        if (FAILED(hr = packages[i]->QueryInterface(&package)) ||
            !(id = get_package_id(package)) ||
            !(version = get_package_version(package)) ||
            !(type = get_package_type(package)) ||
            PyList_Append(res, PyTuple_Pack(3, id, version, type)) < 0)
            goto iter_error;

        package->Release();
        continue;

    iter_error:
        if (package) package->Release();
        Py_XDECREF(version);
        Py_XDECREF(id);

        goto error;
    }

    SafeArrayUnaccessData(sa_packages);
    SafeArrayDestroy(sa_packages);

    return res;
error:
    if (sa_packages && packages) SafeArrayUnaccessData(sa_packages);
    if (sa_packages) SafeArrayDestroy(sa_packages);
    Py_XDECREF(res);

    return error_from_hr(hr);
}

PyObject *find_all_instances()
{
    ISetupConfiguration *sc = nullptr;
    ISetupConfiguration2 *sc2 = nullptr;
    IEnumSetupInstances *enm = nullptr;
    ISetupInstance *inst = nullptr;
    ISetupInstance2 *inst2 = nullptr;
    PyObject *res = nullptr;
    ULONG fetched;
    HRESULT hr;

    if (!(res = PyList_New(0)))
        goto error;

    if (FAILED(hr = CoCreateInstance(
        __uuidof(SetupConfiguration),
        NULL,
        CLSCTX_INPROC_SERVER,
        __uuidof(ISetupConfiguration),
        (LPVOID*)&sc
    )) && hr != REGDB_E_CLASSNOTREG)
        goto error;

    // If the class is not registered, there are no VS instances installed
    if (hr == REGDB_E_CLASSNOTREG)
        return res;

    if (FAILED(hr = sc->QueryInterface(&sc2)) ||
        FAILED(hr = sc2->EnumAllInstances(&enm)))
        goto error;

    while (SUCCEEDED(enm->Next(1, &inst, &fetched)) && fetched) {
        PyObject *id = nullptr;
        PyObject *name = nullptr;
        PyObject *version = nullptr;
        PyObject *path = nullptr;
        PyObject *engine = nullptr;
        PyObject *packages = nullptr;

        if (FAILED(hr = inst->QueryInterface(&inst2)) ||
            !(id = get_instance_id(inst2)) ||
            !(name = get_install_name(inst2)) ||
            !(version = get_install_version(inst)) ||
            !(path = get_install_path(inst)) ||
            !(engine = get_engine_path(inst2)) ||
            !(packages = get_installed_packages(inst2)) ||
            PyList_Append(res, PyTuple_Pack(6, id, name, version, path, engine, packages)) < 0)
            goto iter_error;

        continue;
    iter_error:
        if (inst2) inst2->Release();
        Py_XDECREF(packages);
        Py_XDECREF(engine);
        Py_XDECREF(path);
        Py_XDECREF(version);
        Py_XDECREF(name);
        Py_XDECREF(id);
        goto error;
    }

    enm->Release();
    sc2->Release();
    sc->Release();
    return res;

error:
    if (enm) enm->Release();
    if (sc2) sc2->Release();
    if (sc) sc->Release();
    Py_XDECREF(res);

    return error_from_hr(hr);
}

PyDoc_STRVAR(pyfindvs_findall_doc, "findall()\
\
Finds all installed versions of Visual Studio.");

PyObject *pyfindvs_findall(PyObject *self, PyObject *args, PyObject *kwargs) {
    HRESULT hr = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    if (hr == RPC_E_CHANGED_MODE)
        hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    if (FAILED(hr))
        return error_from_hr(hr);
    PyObject *res = find_all_instances();
    CoUninitialize();
    return res;
}

PyDoc_STRVAR(pyfindvs_getversion_doc, "getversion(path)\
\
Reads the product version from the specified file.");

PyObject *pyfindvs_getversion(PyObject *self, PyObject *args, PyObject *kwargs) {
    LPVOID verblock;
    DWORD verblock_size;

    PyObject *res = NULL;

    PyObject *path_obj;
    const wchar_t *path;
    Py_ssize_t path_len;

    static const char* keywords[] = { "path", NULL };
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O&:getversion", (char**)keywords, PyUnicode_FSDecoder, &path_obj))
        return NULL;

    path = PyUnicode_AsWideCharString(path_obj, &path_len);
    Py_DECREF(path_obj);
    if (!path) {
        return NULL;
    }

    if ((verblock_size = GetFileVersionInfoSizeW(path, NULL)) &&
        (verblock = malloc(verblock_size))) {
        WORD *langinfo;
        wchar_t *verstr;
        UINT langinfo_size, ver_size;

        if (GetFileVersionInfoW(path, 0, verblock_size, verblock) &&
            VerQueryValueW(verblock, L"\\VarFileInfo\\Translation", (LPVOID*)&langinfo, &langinfo_size)) {
            wchar_t rsrc_name[256];
            StringCchPrintfW(rsrc_name, 256, L"\\StringFileInfo\\%04x%04x\\ProductVersion", langinfo[0], langinfo[1]);
            if (VerQueryValueW(verblock, rsrc_name, (LPVOID*)&verstr, &ver_size)) {
                while (ver_size > 0 && !verstr[ver_size]) {
                    ver_size -= 1;
                }
                res = PyUnicode_FromWideChar(verstr, ver_size - 1);
            }
        }
        free(verblock);
    }

    PyMem_Free((void*)path);
    if (!res) {
        Py_RETURN_NONE;
    }
    return res;
}


/*
 * List of functions to add to pyfindvs in exec_pyfindvs().
 */
static PyMethodDef pyfindvs_functions[] = {
    { "findall", (PyCFunction)pyfindvs_findall, METH_VARARGS | METH_KEYWORDS, pyfindvs_findall_doc },
    { "getversion", (PyCFunction)pyfindvs_getversion, METH_VARARGS | METH_KEYWORDS, pyfindvs_getversion_doc },
    { NULL, NULL, 0, NULL } /* marks end of array */
};

/*
 * Initialize pyfindvs. May be called multiple times, so avoid
 * using static state.
 */
int exec_pyfindvs(PyObject *module) {
    PyModule_AddFunctions(module, pyfindvs_functions);

    return 0; /* success */
}

/*
 * Documentation for pyfindvs.
 */
PyDoc_STRVAR(pyfindvs_doc, "The pyfindvs helper module");


static PyModuleDef_Slot pyfindvs_slots[] = {
    { Py_mod_exec, exec_pyfindvs },
    { 0, NULL }
};

static PyModuleDef pyfindvs_def = {
    PyModuleDef_HEAD_INIT,
    "pyfindvs._helper",
    pyfindvs_doc,
    0,              /* m_size */
    NULL,           /* m_methods */
    pyfindvs_slots,
    NULL,           /* m_traverse */
    NULL,           /* m_clear */
    NULL,           /* m_free */
};

PyMODINIT_FUNC PyInit__helper() {
    return PyModuleDef_Init(&pyfindvs_def);
}
