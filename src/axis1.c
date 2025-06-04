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

#include "axis1.h"


// Correct axis1 images by looping over all images correcting for background
int correct_axis_images(uint16_t *in, data_t *out, data_t *bg, data_t *flat,
                        int ndims, index_t *dims) {
    index_t nimages, k;
    int n;

    if (ndims == 2) {
        nimages = 1;
    } else {
        nimages = dims[0];
        for (n = 1; n < (ndims - 2); n++) {
            nimages = nimages * dims[n];
        }
    }

    index_t height = dims[ndims - 2];  // y
    index_t width = dims[ndims - 1];   // x
    index_t imsize = height * width;

#pragma omp parallel for private(k) schedule(static)
    for (index_t img = 0; img < nimages; img++) {
        for (index_t y = 0; y < height; y++) {
            for (index_t x = 0; x < width; x++) {
                index_t in_idx = img * imsize + y * width + x;
                index_t rot_x = height - 1 - y;  // flip rows
                index_t rot_y = x;
                index_t out_idx = img * imsize + rot_y * height + rot_x;  // (N, x, y) layout

                data_t bg_val = bg[y * width + x];
                data_t flat_val = flat[y * width + x];

                if (in[in_idx]) {
                    out[out_idx] = flat_val * ((data_t)(in[in_idx]) - bg_val);
                } else {
                    out[out_idx] = 0.0f;
                }
            }
        }
    }

    return 0;
}


