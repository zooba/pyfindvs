#include <Windows.h>
#include <Setup.Configuration.h>
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "oleaut32.lib")
#pragma comment(lib, "Microsoft.VisualStudio.Setup.Configuration.Native.lib")

#include <Python.h>

PyObject *error_from_hr(HRESULT hr)
{
    if (FAILED(hr))
        PyErr_Format(PyExc_OSError, "Error %08x", hr);
    assert(PyErr_Occurred());
    return nullptr;
}

PyObject *get_install_name(ISetupInstance2 *inst)
{
    HRESULT hr;
    BSTR name;
    PyObject *str = nullptr;
    if (FAILED(hr = inst->GetDisplayName(LOCALE_USER_DEFAULT, &name)))
        goto error;
    str = PyUnicode_FromWideChar(name, SysStringLen(name));
    SysFreeString(name);
    return str;
error:

    return error_from_hr(hr);
}

PyObject *get_install_version(ISetupInstance *inst)
{
    HRESULT hr;
    BSTR ver;
    PyObject *str = nullptr;
    if (FAILED(hr = inst->GetInstallationVersion(&ver)))
        goto error;
    str = PyUnicode_FromWideChar(ver, SysStringLen(ver));
    SysFreeString(ver);
    return str;
error:

    return error_from_hr(hr);
}

PyObject *get_install_path(ISetupInstance *inst)
{
    HRESULT hr;
    BSTR path;
    PyObject *str = nullptr;
    if (FAILED(hr = inst->GetInstallationPath(&path)))
        goto error;
    str = PyUnicode_FromWideChar(path, SysStringLen(path));
    SysFreeString(path);
    return str;
error:

    return error_from_hr(hr);
}

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
        BSTR id = nullptr;
        PyObject *str = nullptr;

        if (FAILED(hr = packages[i]->QueryInterface(&package)) ||
            FAILED(hr = package->GetId(&id)))
            goto iter_error;

        str = PyUnicode_FromWideChar(id, SysStringLen(id));
        SysFreeString(id);

        if (!str || PyList_Append(res, str) < 0)
            goto iter_error;

        Py_CLEAR(str);
        package->Release();
        continue;

    iter_error:
        if (package) package->Release();
        Py_XDECREF(str);

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
        PyObject *name = nullptr;
        PyObject *version = nullptr;
        PyObject *path = nullptr;
        PyObject *packages = nullptr;

        if (FAILED(hr = inst->QueryInterface(&inst2)) ||
            !(name = get_install_name(inst2)) ||
            !(version = get_install_version(inst)) ||
            !(path = get_install_path(inst)) ||
            !(packages = get_installed_packages(inst2)) ||
            PyList_Append(res, PyTuple_Pack(4, name, version, path, packages)) < 0)
            goto iter_error;

        continue;
    iter_error:
        if (inst2) inst2->Release();
        Py_XDECREF(packages);
        Py_XDECREF(path);
        Py_XDECREF(version);
        Py_XDECREF(name);
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

/*
 * List of functions to add to pyfindvs in exec_pyfindvs().
 */
static PyMethodDef pyfindvs_functions[] = {
    { "findall", (PyCFunction)pyfindvs_findall, METH_VARARGS | METH_KEYWORDS, pyfindvs_findall_doc },
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
