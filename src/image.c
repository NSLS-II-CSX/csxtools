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

void rotate90fast(data_t *in, data_t *out, int ndims, index_t *dims, int sense){
  index_t nimages = dims[0];
  index_t M = dims[ndims-1];
  index_t N = dims[ndims-2];
  index_t imsize = M * N;
  int i;
  for(i=1;i<(ndims-2);i++){
    nimages = nimages * dims[i];
  }   

  // First lets setup a translation mask.
  
  index_t *map = malloc(sizeof(index_t) * imsize);
  if(!map){
    return;
  }

  // Remember:
  // x' = x cos T - y sin T
  // y' = x sin T + y cos T
  //
  // x' = -y 
  // y' = x

  int n, m;
  data_t *outp = out;
  for(n=0;n<N;n++){
    for(m=0;m<M;m++){
      //*outp = m*      
    }
  }
}

void rotate90(data_t *in, data_t *out, int ndims, index_t *dims, int sense){
  index_t nimages = dims[0];
  index_t M = dims[ndims-1];
  index_t N = dims[ndims-2];
  index_t imsize = N*M;

  int x;
  for(x=1;x<(ndims-2);x++){
    nimages = nimages * dims[x];
  }   

  index_t *map = malloc(sizeof(index_t) * imsize);
  if(!map){
    return;
  }

  index_t i;
#pragma omp parallel for shared(map,N,M,imsize) private(i)
  for(i=0;i<imsize;i++){
    index_t *mapp = map + i;
    index_t a, b;
    if(sense){
      a = M - 1 - (i / N);
      b = i % N;
    } else {
      a = i / N;
      b = N - 1 - (i % N);
    }
    *mapp = M*b + a;
  }

  index_t n;
#pragma omp parallel for shared(in,out,map,imsize,nimages) private(n)
  for(n=0;n<(nimages*imsize);n++){
    data_t *inp = in + (imsize * (n / imsize));
    data_t *outp = out + n;
    index_t *mapp = map + (n % imsize);
    *outp = inp[*mapp];
  }

  free(map);
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
