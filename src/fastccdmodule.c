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

#include "fastccd.h"

static PyObject* fastccd_correct_images(PyObject *self, PyObject *args){
  PyObject *_input = NULL;
  PyObject *_bgnd = NULL;
  PyArrayObject *input = NULL;
  PyArrayObject *bgnd = NULL;
  PyArrayObject *out = NULL;
  npy_intp *dims;
  int ndims;


  if(!PyArg_ParseTuple(args, "OO", &_input, &_bgnd)){
    return NULL;
  }

  input = (PyArrayObject*)PyArray_FROM_OTF(_input, NPY_UINT16, NPY_ARRAY_IN_ARRAY);
  if(!input){
    goto error;
  }
  bgnd = (PyArrayObject*)PyArray_FROM_OTF(_bgnd, NPY_FLOAT, NPY_ARRAY_IN_ARRAY);
  if(!bgnd){
    goto error;
  }

  ndims = PyArray_NDIM(input);
  dims = PyArray_DIMS(input);

  out = (PyArrayObject*)PyArray_SimpleNew(ndims, dims, NPY_FLOAT);
  if(!out){
    goto error;
  }
   
  correct_fccd_images((uint16_t*)PyArray_DATA(input), 
                      (data_t*)PyArray_DATA(out),
                      (data_t*)PyArray_DATA(bgnd),
                      ndims, (index_t*)dims);

  Py_XDECREF(input);
  Py_XDECREF(bgnd);
  return Py_BuildValue("N", out);

error:
  Py_XDECREF(input);
  Py_XDECREF(bgnd);
  Py_XDECREF(out);
  return NULL;
}

static PyMethodDef FastCCDMethods[] = {
  { "correct_images", fastccd_correct_images, METH_VARARGS,
    "Correct FastCCD Images"},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef fastccdmodule = {
   PyModuleDef_HEAD_INIT,
   "fastccd",   /* name of module */
   NULL,        /* module documentation, may be NULL */
   -1,          /* size of per-interpreter state of the module,
                   or -1 if the module keeps state in global variables. */
   FastCCDMethods
};

PyMODINIT_FUNC PyInit_fastccd(void) {
  PyObject *m;
  m = PyModule_Create(&fastccdmodule);
  if(m == NULL){
    return NULL;
  }

  import_array();
  import_umath();

  return m;
}
