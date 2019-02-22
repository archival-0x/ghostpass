#include <stdint.h>
#include <python2.7/Python.h>

/* available functions for interface */
static PyObject* expand_decimal(PyObject *self, PyObject *args);

/* module specification */
static PyMethodDef module_methods[] = {
    {"expand_decimal", expand_decimal, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

/* module initialization */
PyMODINIT_FUNC initcpuid(void)
{
    (void) Py_InitModule("bitexpand", module_methods);
}

/* helper method for bit expansion on converted uint8_t */
static uint32_t bit_expand(uint8_t in_val)
{
    /* takes an 8-bit value and converts it into a 24-bit one */
    uint32_t out_val;
    out_val = (((in_val * 0x101 & 0x0F00F) * 0x11 & 0x0C30C3) * 5 & 0x249249) * 7;

    /* since an expansion factor of 3 is applied, there is going to be padding */
    return out_val;
}


/* main method for bit expansion */
static PyObject* expand_decimal(PyObject *self, PyObject *args)
{
    return PyBuildValue("[i, i, i]", );
}
