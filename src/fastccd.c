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

#include "fastccd.h"


// Correct fast ccd images by looping over all images correcting for background
int correct_fccd_images(uint16_t *in, data_t *out, data_t *bg, data_t *flat,
                        int ndims, index_t *dims, data_t* gain){
  index_t nimages,k;
  int n;

  if(ndims == 2)
  {
    nimages = 1;
  } else {
    nimages = dims[0];
    for(n=1;n<(ndims-2);n++){
      nimages = nimages * dims[n];
    }   
  }

  index_t imsize = dims[ndims-1] * dims[ndims-2];

#pragma omp parallel for private(k) shared(in, out, bg, imsize, gain, flat) schedule(static,imsize)
  for(k=0;k<nimages*imsize;k++){
    // Reset the background pointer each time
    data_t *bgp = bg + (k % imsize);
    data_t *flatp = flat + (k % imsize);
    //
    // Note GAIN_1 is the least sensitive setting which means we need to multiply the
    // measured values by 8. Conversly GAIN_8 is the most sensitive and therefore only
    // does not need a multiplier
    //
    if((in[k] & BAD_PIXEL) == BAD_PIXEL){
      out[k] = NAN;
    } else if((in[k] & GAIN_1) == GAIN_1){
      out[k] = *flatp * gain[2] * ((data_t)(in[k] & PIXEL_MASK) - *(bgp + 2 * imsize));
    } else if((in[k] & GAIN_2) == GAIN_2){
      out[k] = *flatp * gain[1] * ((data_t)(in[k] & PIXEL_MASK) - *(bgp + imsize));
    } else {
      out[k] = *flatp * gain[0] * ((data_t)(in[k] & PIXEL_MASK) - *bgp);
    }
  }

  return 0;
}

