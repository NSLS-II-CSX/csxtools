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
#include <numpy/ndarrayobject.h>

#include "phocount.h"

static PyObject* phocount_count(PyObject *self, PyObject *args){
  PyObject *_input = NULL;
  PyArrayObject *input = NULL;
  PyArrayObject *stddev = NULL;
  PyArrayObject *out = NULL;
  npy_intp *dims;
  int ndims;
  float thresh[2], sum_filter[2], std_filter[2];
  int sum_max;
  int nan = 0;

  if(!PyArg_ParseTuple(args, "O(ff)(ff)(ff)i|p", &_input, &thresh[0], &thresh[1],
                                             &sum_filter[0], &sum_filter[1], 
                                             &std_filter[0], &std_filter[1], 
                                             &sum_max, &nan)){
    return NULL;
  }

  if(sum_max <= 0 || sum_max > 9){
    PyErr_SetString(PyExc_ValueError, "Maximum sum value must be between 0 and 9");
    goto error;
  }

  input = (PyArrayObject*)PyArray_FROMANY(_input, NPY_FLOAT, 3, 0,NPY_ARRAY_IN_ARRAY);
  if(!input){
    goto error;
  }

  ndims = PyArray_NDIM(input);
  dims = PyArray_DIMS(input);

  out = (PyArrayObject*)PyArray_SimpleNew(ndims, dims, NPY_FLOAT); 
  if(!out){
    goto error;
  }

  stddev = (PyArrayObject*)PyArray_SimpleNew(ndims, dims, NPY_FLOAT);
  if(!stddev){
    goto error;
  }
  
  data_t *input_p = (data_t*)PyArray_DATA(input); 
  data_t *out_p = (data_t*)PyArray_DATA(out);
  data_t *stddev_p = (data_t*)PyArray_DATA(stddev);

  // Ok now we don't touch Python Object ... Release the GIL
  Py_BEGIN_ALLOW_THREADS
  
  count(input_p, out_p, stddev_p, ndims, dims, thresh, 
        sum_filter, std_filter, sum_max, nan);

  Py_END_ALLOW_THREADS

  Py_XDECREF(input);
  return Py_BuildValue("(NN)", out, stddev);

error:
  Py_XDECREF(input);
  Py_XDECREF(out);
  Py_XDECREF(stddev);
  return NULL;
}

static PyMethodDef phocountMethods[] = {
  { "count", phocount_count, METH_VARARGS,
    "Identify and count photons in CCD image"},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef phocountmodule = {
   PyModuleDef_HEAD_INIT,
   "phocount",     /* name of module */
   NULL,        /* module documentation, may be NULL */
   -1,          /* size of per-interpreter state of the module,
                   or -1 if the module keeps state in global variables. */
   phocountMethods
};

PyMODINIT_FUNC PyInit_phocount(void) {
  PyObject *m;
  m = PyModule_Create(&phocountmodule);
  if(m == NULL){
    return NULL;
  }

  import_array();

  return m;
}
