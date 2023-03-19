#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "tray.h"

#define TRAY_ICON1 "icon.ico"


static PyObject* py_options_cb = NULL;
static PyObject* py_screenshot_cb = NULL;
static PyObject* py_quit_cb = NULL;
PyObject *result;

static void options_cb(struct tray_menu *item){
    (void)item;
    PyObject_CallObject(py_options_cb,NULL);
}


static void quit_cb(struct tray_menu *item) {
  (void)item;
  tray_exit();
  PyObject_CallObject(py_quit_cb,NULL);
}    

static void tray_cb() {
    PyObject_CallObject(py_screenshot_cb, NULL);
}

static struct tray tray = {
    .icon = TRAY_ICON1,
    .menu =
        (struct tray_menu[]){
            {.text = "Options", .cb= options_cb},
            {.text = "-"},
            {.text = "Quit", .cb = quit_cb}},
    .cb = tray_cb
};

static PyObject* create_tray(PyObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject* tmp_scr_cb;
    PyObject* tmp_opt_cb;
    PyObject* tmp_quit_cb;
    static char* keywords[] = {"screenshot_callback","options_callback","quit_callback", NULL};
    

    if(PyArg_ParseTupleAndKeywords(args, kwargs, "OOO", keywords, &tmp_scr_cb, &tmp_opt_cb, &tmp_quit_cb))
    {
        if (!PyCallable_Check(tmp_scr_cb) ||
            !PyCallable_Check(tmp_opt_cb) ||
            !PyCallable_Check(tmp_quit_cb)) 
        {
            PyErr_SetString(PyExc_TypeError, "parameter must be callable");
            Py_RETURN_NONE;
        }

        Py_XINCREF(tmp_scr_cb);
        Py_XDECREF(py_screenshot_cb);
        py_screenshot_cb = tmp_scr_cb;
        

        Py_XINCREF(tmp_opt_cb);
        Py_XDECREF(py_options_cb);
        py_options_cb = tmp_opt_cb;

        Py_XINCREF(tmp_quit_cb);
        Py_XDECREF(py_quit_cb);
        py_quit_cb = tmp_quit_cb;
    } 

    if (tray_init(&tray) < 0) {
        PyErr_SetString(PyExc_RuntimeError, "failed to create tray");
        Py_RETURN_NONE;
    }

    while (tray_loop(1) != -1);
    Py_RETURN_NONE;
}

static PyMethodDef TrayMethods[] = {
    {"create_tray",  create_tray, METH_VARARGS | METH_KEYWORDS,
     "Execute a shell command."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef traymodule = {
    PyModuleDef_HEAD_INIT,
    "tray",
    NULL,
    -1,
    TrayMethods
};

PyMODINIT_FUNC PyInit_tray(void)
{
    return PyModule_Create(&traymodule);
}

int main(int argc, char *argv[])
{
    wchar_t *program = Py_DecodeLocale(argv[0], NULL);
    if (program == NULL) {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
        exit(1);
    }

    if (PyImport_AppendInittab("tray", PyInit_tray) == -1) {
        fprintf(stderr, "Error: could not extend in-built modules table\n");
        exit(1);
    }

    Py_SetProgramName(program);

    Py_Initialize();

    PyObject *pmodule = PyImport_ImportModule("tray");
    if (!pmodule) {
        PyErr_Print();
        fprintf(stderr, "Error: could not import module 'tray'\n");
    }

    PyMem_RawFree(program);
    return 0;
}