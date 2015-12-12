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

#include <omp.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <stdint.h>

#include "image.h"

void rotate90(data_t *in, data_t *out, int ndims, index_t *dims, int sense){
  index_t nimages = dims[0];
  index_t imsize = dims[ndims-1] * dims[ndims-2];

  int n;
  for(n=1;n<(ndims-2);n++){
    nimages = nimages * dims[n];
  }   

  index_t M = dims[ndims-1];
  index_t N = dims[ndims-2];

  transpose(in, out, nimages, imsize, M, N);
  // Remember ! we now have a N x M array not M x N
  if(!sense){
    fliprows(out, nimages, N, M);
  } else {
    flipcols(out, nimages, N, M);
  }
}

void transpose(data_t *in, data_t *out, index_t nimages, index_t imsize, index_t M, index_t N){

  index_t n;
#pragma omp parallel for shared(N,M,in,out,imsize) private(n)
  for(n=0;n<nimages;n++){
    data_t *inp = in + (n * imsize);
    data_t *outp = out + (n * imsize);
    index_t i;
    for(i=0;i<imsize;i++){
      index_t a = i / N;
      index_t b = i % N;
      *outp = inp[M*b + a];
      outp++;
    }
  }
}

void fliprows(data_t *data, index_t nimages, index_t M, index_t N){
  index_t n;
#pragma omp parallel for shared(data, N, M) private (n)
  for(n=0;n<(nimages*N);n++){
    data_t *datap = data + (n * M);
    index_t i;
    for(i=0;i<M/2;i++){
      data_t temp = datap[i];
      datap[i] = datap[M-i-1];
      datap[M-i-1] = temp;
    }
  }
}

void flipcols(data_t *data, index_t nimages, index_t M, index_t N){
  index_t n;
#pragma omp parallel for shared(data, N, M) private (n)
  for(n=0;n<(nimages*M);n++){
    data_t *datap = data + n%M + (n/M)*(N*M);
    index_t i;
    for(i=0;i<N/2;i++){
      data_t temp = datap[i*M];
      datap[i*M] = datap[M * (N-i-1)];
      datap[M * (N-i-1)] = temp;
    }
  }
}
