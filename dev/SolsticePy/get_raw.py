import numpy as N
import re
import sys
import os
from uncertainties import ufloat
from uncertainties.umath import * 

def proces_raw_results(rawfile, savedir,rho_mirror):

    '''
    rawfile - the 'simul' file that generated by SOLSTICE
    savedir - the directy for saving the organised results
    '''
    with open(rawfile) as f:
        content = f.read().splitlines()
        # content is a list with lots of string
    f.close()

    results=N.array([])

    # sun direction
    sun=re.findall("[-+]?\d*\.\d+|\d+", content[0])
    azimuth=sun[0]
    elevation=sun[1]

    # Global results
    line=map(float, content[1].split(' '))
    num_hst=line[2]
    num_rays=line[3]

    potential=map(float, content[2].split(' '))[0] #W
    potential_err=map(float, content[2].split(' '))[1]

    absorbed=map(float, content[3].split(' '))[0]
    absorbed_err=map(float, content[3].split(' '))[1]    

    Fcos=map(float, content[4].split(' '))[0]
    Fcos_err=map(float, content[4].split(' '))[1]  

    shadow_loss=map(float, content[5].split(' '))[0]
    shadow_err=map(float, content[5].split(' '))[1]    
  
    missing_loss=map(float, content[6].split(' '))[0]
    missing_err=map(float, content[6].split(' '))[1] 

    material_loss=map(float, content[7].split(' '))[0]
    material_err=map(float, content[7].split(' '))[1]    
   
    atmospheric_loss=map(float, content[8].split(' '))[0]
    atmospheric_err=map(float, content[8].split(' '))[1]  


    # Target (receiver)
    target=content[9].split()
    rec_area=float(target[2]) # m2  
    rec_income=float(target[3])
    rec_income_err=float(target[4])
    #rec_no_material_loss=float(target[5])
    #rec_no_material_loss_err=float(target[6])
    #rec_no_atmo_loss=float(target[7])
    #rec_no_atmo_loss_err=float(target[8])
    #rec_material_loss=float(target[9])
    #rec_material_loss_err=float(target[10])
    rec_absorbed=float(target[13])
    rec_absorbed_err=float(target[14])
    rec_eff=float(target[23])
    rec_eff_err=float(target[24])


    #Virtual target
    virtual=content[10].split()
    vir_area=float(virtual[2])
    vir_income=float(virtual[3])
    vir_income_err=float(virtual[4])
    
    

    
    raw_res=N.array(['name','value', 'error',
                     'sun_azimuth', azimuth,'',
                     'sun_elevation', elevation, '',
                     'num hst', num_hst,'', 
                     'num rays',num_rays, '',
                     'potential flux', potential, potential_err,
                     'absorbed flux', absorbed, absorbed_err, 
                     'Cosine factor', Fcos, Fcos_err, 
                     'shadow loss', shadow_loss, shadow_err, 
                     'Mising loss', missing_loss, missing_err, 
                     'materials loss', material_loss, material_err,
                     'atomospheric loss', atmospheric_loss, atmospheric_err, 
                     '','','',
                     'Target', '','',
                     'area', rec_area, '',
                     'Incoming flux', rec_income, rec_income_err, 
                     'absorbed flux', rec_absorbed, rec_absorbed_err, 
                     'efficiency', rec_eff, rec_eff_err,
                      '','','',
                      'Virtual plane','','',
                      'area', vir_area, '',
                      'income flux', vir_income,vir_income_err])
    
    raw_res=raw_res.reshape(len(raw_res)/3, 3)

    N.savetxt(savedir+'/result-raw.csv', raw_res, fmt='%s', delimiter=',')

 
    Qtotal=ufloat(potential, 0)
    Fcos=ufloat(Fcos,Fcos_err) 
    Qcos=Qtotal*(1.-Fcos)
    Qshade=ufloat(shadow_loss,shadow_err)
    Qfield_abs=(Qtotal-Qcos-Qshade)*(1.-float(rho_mirror))
    Qatm=ufloat(atmospheric_loss, atmospheric_err)
    Qspil=ufloat(vir_income,vir_income_err)
    Qabs=ufloat(rec_absorbed, rec_absorbed_err)
    Qrefl=ufloat(rec_income,rec_income_err)-Qabs
    Qblock=Qtotal-Qcos-Qshade-Qfield_abs-Qspil-Qabs-Qrefl-Qatm

    
    organised=N.array(['Name', 'Value', '+/-Error', 
                       'Qall (kW)', Qtotal.n/1000., Qtotal.s/1000., 
                       'Qcos (kW)', Qcos.n/1000.,Qcos.s/1000.,
                       'Qshad (kW)', Qshade.n/1000., Qshade.s/1000.,
                       'Qfield_abs (kW)', Qfield_abs.n/1000., Qfield_abs.s/1000., 
                       'Qblcok (kW)', Qblock.n/1000.,  Qblock.s/1000., 
                       'Qatm (kW)',Qatm.n/1000., Qatm.s/1000., 
                       'Qspil (kW)', Qspil.n/1000., Qspil.s/1000., 
                       'Qrefl (kW)', Qrefl.n/1000.,Qrefl.s/1000., 
                       'Qabs (kW)', Qabs.n/1000., Qabs.s/1000., 
                       'rays', num_rays,'-'])
    N.savetxt(savedir+'/result-formatted.csv', organised.reshape(len(organised)/3,3), fmt='%s', delimiter=',')
    
    efficiency_total=Qabs/Qtotal
    print ''
    print 'Total efficiency:', efficiency_total

    return efficiency_total
    
  


if __name__=='__main__':
    
    proces_raw_results(sys.argv[1], sys.argv[2], sys.argv[3])


