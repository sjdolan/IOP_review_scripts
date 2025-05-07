import ROOT
import os
from ROOT import gStyle, TGaxis, TPad, TLine, gROOT, TH1, TColor, TCanvas, TFile, TH1D, gPad, TLegend, kWhite, gDirectory, gEnv
from glob import glob

from plotting_functions import make_generator_comp
## def make_generator_comp(outPlotName, inFileList, nameList, colzList, \
##                         plotVar="q0", binning="100,0,5", cut="cc==1", \
##                         labels="q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/nucleon)",
##                         legDim=[0.65, 0.5, 0.85, 0.93], ratLimits=[0.4, 1.6], maxVal=None, isShape=False)


## Use double precision for TTree draw
gEnv.SetValue("Hist.Precision.1D", "double")

## No need to see the plots appear here
gROOT.SetBatch(1)
gStyle.SetLineWidth(3)
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetOptFit(0)
TGaxis.SetMaxDigits(4)

gStyle.SetTextSize(0.05)
gStyle.SetLabelSize(0.05,"xyzt")
gStyle.SetTitleSize(0.05,"xyzt")

gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)
gStyle.SetNdivisions(505, "XY")

gROOT .ForceStyle()

TH1.SetDefaultSumw2()
gStyle.SetLineWidth(3)

## Sort out the position of the y axis exponent...
TGaxis.SetExponentOffset(-0.06, 0., "y")

def make_T2K_erec_plots(inputDir="inputs/"):

    nameList = ["GENIE 10a",\
                "GENIE 10b",\
                "GENIE 10c",\
                "CRPA",\
                "SuSAv2",\
                "NEUT",\
                "NuWro"\
                ]
    colzList = [9000, 9001, 9002, 9003, 9004, 9006, 9005]
    
    ## QE reco
    qe_cut = "cc==1 && Sum$(abs(pdg) > 100 && abs(pdg) < 2000)==0 && Sum$(abs(pdg) > 2300 && abs(pdg) < 100000)==0 && Sum$(pdg==2212) > 0"

    ## Loop over configs
    for det in ["T2KND", "T2KSK_osc"]:
        for flux in ["FHC_numu", "RHC_numubar"]:
            ## These files can be found here (no login required): https://portal.nersc.gov/project/dune/data/2x2/simulation
            inFileList = [inputDir+"/"+det+"_"+flux+"_H2O_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_H2O_GENIEv3_G18_10b_00_000_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_H2O_GENIEv3_G18_10c_00_000_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_H2O_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_H2O_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_H2O_NEUT562_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_H2O_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                          ]
            
            make_generator_comp(det+"_"+flux+"_H2O_EnuQE_gencomp.pdf", inFileList, nameList, colzList, "Enu_QE", "80,0,2", qe_cut, \
                                "E_{#nu}^{rec, QE} (GeV); d#sigma/dE_{#nu}^{rec, QE} (#times 10^{-38} cm^{2}/nucleon)")

            make_generator_comp(det+"_"+flux+"_H2O_EnuQEbias_gencomp.pdf", inFileList, nameList, colzList, "(Enu_QE - Enu_true)/Enu_true", "80,-1,1", qe_cut, \
                                "(E_{#nu}^{rec, QE} - E_{#nu}^{true})/E_{#nu}^{true}; Arb. norm.", isShape=True)
            
def make_DUNE_erec_plots(inputDir="inputs/"):

    nameList = ["GENIE 10a",\
                "GENIE 10b",\
                "GENIE 10c",\
                "CRPA",\
                "SuSAv2",\
                "NEUT",\
                "NuWro"\
                ]
    colzList = [9000, 9001, 9002, 9003, 9004, 9006, 9005]
    
    ## QE reco
    ehad_cut = "cc==1"
    enuhad = "ELep + Sum$((abs(pdg)==11 || (abs(pdg)>17 && abs(pdg)<2000))*E) + Sum$((abs(pdg)>2300 &&abs(pdg)<10000)*E) + Sum$((abs(pdg)==2212)*(E - sqrt(E*E - px*px - py*py - pz*pz)))"

    ## Loop over configs
    for det in ["DUNEND", "DUNEFD_osc"]:
        for flux in ["FHC_numu", "RHC_numubar"]:
            ## These files can be found here (no login required): https://portal.nersc.gov/project/dune/data/2x2/simulation
            inFileList = [inputDir+"/"+det+"_"+flux+"_Ar40_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_Ar40_GENIEv3_G18_10b_00_000_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_Ar40_GENIEv3_G18_10c_00_000_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_Ar40_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_Ar40_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_Ar40_NEUT562_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_Ar40_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                          ]
            
            make_generator_comp(det+"_"+flux+"_Ar40_Enurec_gencomp.pdf", inFileList, nameList, colzList, enuhad, "80,0,8", ehad_cut, \
                                "E_{#nu}^{rec, had} (GeV); d#sigma/dE_{#nu}^{rec, had} (#times 10^{-38} cm^{2}/nucleon)")

            make_generator_comp(det+"_"+flux+"_Ar40_Enurecbias_gencomp.pdf", inFileList, nameList, colzList, "("+enuhad+" - Enu_true)/Enu_true", "70,-0.5,0.2", ehad_cut, \
                                "(E_{#nu}^{rec, had} - E_{#nu}^{true})/E_{#nu}^{true}; Arb. norm.",  [0.25, 0.5, 0.45, 0.93], yRatLimits=[0,2.2], isShape=True)

if __name__ == "__main__":

    inputDir="/global/cfs/cdirs/dune/users/cwilk/MC_IOP_review/*/"
    #make_T2K_erec_plots(inputDir)
    make_DUNE_erec_plots(inputDir)

