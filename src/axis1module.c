/*
 * Copyright (c) 2014, Brookhaven Science Associates, Brookhaven        
 * National Laboratory. All rights reserved.                            
 *                                                                      
 * Redistribution and use in source and binary forms, with or without   
 * modification, are permitted provided that the following conditions   
 * are met:                                                             
 *                                                                      
 * * Redistributions of source code must retain the above copyright     
 *   notice, this list of conditions and the following disclaimer.      
 *                                                                      
 * * Redistributions in binary form must reproduce the above copyright  
 *   notice this list of conditions and the following disclaimer in     
 *   the documentation and/or other materials provided with the         
 *   distribution.                                                      
 *                                                                      
 * * Neither the name of the Brookhaven Science Associates, Brookhaven  
 *   National Laboratory nor the names of its contributors may be used  
 *   to endorse or promote products derived from this software without  
 *   specific prior written permission.                                 
 *                                                                      
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS  
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT    
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS    
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE       
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,           
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES   
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR   
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)   
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,  
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OTHERWISE) ARISING   
 * IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE   
 * POSSIBILITY OF SUCH DAMAGE.                                          
 *
 */

#include <stdio.h>
#include <Python.h>

/* Include python and numpy header files */
#include <math.h>
#define NPY_NO_DEPRECATED_API NPY_1_9_API_VERSION
#include <numpy/ndarraytypes.h>
#include <numpy/ufuncobject.h>

#include "axis1.h"

static PyObject* axis1_correct_images(PyObject *self, PyObject *args){
  PyObject *_input = NULL;
  PyObject *_bgnd = NULL;
  PyObject *_flat = NULL;
  PyArrayObject *input = NULL;
  PyArrayObject *bgnd = NULL;
  PyArrayObject *flat = NULL;
  PyArrayObject *out = NULL;
  npy_intp *dims;
  npy_intp *dims_bgnd;
  npy_intp *dims_flat;
  int ndims;

  if(!PyArg_ParseTuple(args, "OOO", &_input, &_bgnd, &_flat)){   
    return NULL;
  }
  
  input = (PyArrayObject*)PyArray_FROMANY(_input, NPY_UINT16, 2, 0,NPY_ARRAY_IN_ARRAY);
  if(!input){
    goto error;
  }

  bgnd = (PyArrayObject*)PyArray_FROMANY(_bgnd, NPY_FLOAT, 2, 2, NPY_ARRAY_IN_ARRAY);
  if(!bgnd){
    goto error;
  }

  flat = (PyArrayObject*)PyArray_FROMANY(_flat, NPY_FLOAT, 2,2, NPY_ARRAY_IN_ARRAY);
  if(!flat){
    goto error;
  }

  ndims = PyArray_NDIM(input);
  dims = PyArray_DIMS(input);
  dims_bgnd = PyArray_DIMS(bgnd);
  dims_flat = PyArray_DIMS(flat);

  // Check array dimensions for dark and flat
  if(dims[ndims-2] != dims_bgnd[0] || dims[ndims-1] != dims_bgnd[1]){
    PyErr_SetString(PyExc_ValueError, "Dimensions of image array do not match background array dimensions.");
    goto error;
  }
  if(dims[ndims-2] != dims_flat[0] || dims[ndims-1] != dims_flat[1]){
    PyErr_SetString(PyExc_ValueError, "Dimensions of image array do not match flat-field array dimensions.");
    goto error;
  }
    
  out = (PyArrayObject*)PyArray_SimpleNew(ndims, dims, NPY_FLOAT);
  if(!out){
    goto error;
  }

  uint16_t* input_p = (uint16_t*)PyArray_DATA(input);
  data_t *out_p = (data_t*)PyArray_DATA(out);
  data_t *bgnd_p = (data_t*)PyArray_DATA(bgnd);
  data_t *flat_p = (data_t*)PyArray_DATA(flat);
   
  // Ok now we don't touch Python Object ... Release the GIL
  Py_BEGIN_ALLOW_THREADS

  correct_axis_images(input_p, out_p, bgnd_p, flat_p,
		      ndims, (index_t*)dims);
  
  Py_END_ALLOW_THREADS

  Py_XDECREF(input);
  Py_XDECREF(bgnd);
  Py_XDECREF(flat);
  return Py_BuildValue("N", out);

error:
  Py_XDECREF(input);
  Py_XDECREF(bgnd);
  Py_XDECREF(out);
  Py_XDECREF(flat);
  return NULL;
}

static PyMethodDef AXIS1_Methods[] = {
  { "correct_images_axis", axis1_correct_images, METH_VARARGS,
    "Correct AXIS1 Images"},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef axis1module = {  
   PyModuleDef_HEAD_INIT,
   "axis1",     /* name of module */
   NULL,        /* module documentation, may be NULL */
   -1,          /* size of per-interpreter state of the module,
                   or -1 if the module keeps state in global variables. */
   AXIS1_Methods
};

PyMODINIT_FUNC PyInit_axis1(void) {
  PyObject *m;
  m = PyModule_Create(&axis1module);
  if(m == NULL){
    return NULL;
  }

  import_array();
  import_umath();

  return m;
}
