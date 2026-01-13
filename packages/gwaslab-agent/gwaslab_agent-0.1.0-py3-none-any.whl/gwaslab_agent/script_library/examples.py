 # Perform basic quality control to ensure data integrity before plotting                                          
 sumstats.basic_check()                                                                                            
                                                                                                                   
 # Filter for lead variants on odd chromosomes with significance level of 1e-2                                     
 # First, get lead variants across the genome at the specified significance threshold                              
 leads_df = sumstats.get_lead(sig_level=1e-2)                                                                      
                                                                                                                   
 # Filter lead variants to keep only those on odd chromosomes (1, 3, 5, ..., 25)                                   
 odd_chromosome_leads = leads_df[leads_df['CHR'] % 2 == 1]                                                         
                                                                                                                   
 # Extract the SNPIDs of lead variants on odd chromosomes for highlighting                                         
 highlight_snps = odd_chromosome_leads['SNPID'].tolist()                                                           
                                                                                                                   
 # Create Manhattan plot without QQ plot, highlighting lead variants on odd chromosomes                            
 # Using larger marker size and font size as requested                                                             
 sumstats.plot_manhattan(                                                                                          
     mode='m',  # Manhattan plot only (no QQ plot)                                                                 
     highlight=highlight_snps,  # Highlight lead variants on odd chromosomes                                       
     highlight_windowkb=500,  # 500 kb window for highlighting                                                     
     fontsize=14,  # Larger font size                                                                              
     fig_kwargs={'figsize': (16, 8)},  # Larger figure size                                                        
     mtitle="Manhattan Plot with Lead Variants on Odd Chromosomes Highlighted",                                    
     sig_level=1e-2,                                                                                               
     anno_fontsize=12,                                                                                             
     arm_scale=1.5                                                                                                 
 )      