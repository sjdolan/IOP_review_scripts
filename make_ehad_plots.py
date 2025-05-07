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
gStyle.SetLineStyleString(11,"40 20 40 20")
gStyle.SetLineStyleString(12,"20 10 20 10")

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

ccinc = "cc==1"
cc0pi = "cc==1 && Sum$(abs(pdg) > 100 && abs(pdg) < 2000)==0 && Sum$(abs(pdg) > 2300 && abs(pdg) < 100000)==0 && Sum$(pdg==2212) > 0"
ehad = "Sum$((abs(pdg)==11 || (abs(pdg)>17 && abs(pdg)<2000))*E) + Sum$((abs(pdg)>2300 &&abs(pdg)<10000)*E) + Sum$((abs(pdg)==2212)*(E - 0.938))"


def make_q0_plots(inputDir="inputs/"):

    nameList = ["GENIE 10a",\
                "CRPA",\
                "SuSAv2",\
                "NEUT",\
                "NuWro"\
                ]
    colzList = [9000, 9003, 9004, 9006, 9005]

    ## DUNE plots
    det   = "DUNEND"
    targ  = "Ar40"
    for flux in ["FHC_numu", "RHC_numubar"]:
        inFileList = [inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_NEUT562_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                      ]
        make_generator_comp(det+"_"+flux+"_"+targ+"_q0_gencomp.pdf", inFileList, nameList, colzList, "q0", "100,0,2", ccinc, \
                            "q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/GeV/nucleon)", [0.65, 0.6, 0.85, 0.93])

    ## Now T2K
    det   = "T2KND"
    targ  = "H2O"
    for flux in ["FHC_numu", "RHC_numubar"]:
        inFileList = [inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_NEUT562_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                      ]	
        make_generator_comp(det+"_"+flux+"_"+targ+"_q0_gencomp.pdf", inFileList, nameList, colzList, "q0", "100,0,1", cc0pi, \
                            "q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/GeV/nucleon)", [0.65, 0.6, 0.85, 0.93])


def make_ehad_plots(inputDir="inputs/"):

    nameList = ["GENIE 10a",\
                "GENIE 10b",\
                "GENIE 10c",\
                "CRPA",\
                "SuSAv2",\
                "NEUT",\
                "NuWro"\
                ]
    colzList = [9000, 9001, 9002, 9003, 9004, 9006, 9005]

    ## DUNE plots
    det   = "DUNEND"
    targ  = "Ar40"
    for flux in ["FHC_numu", "RHC_numubar"]:
        inFileList = [inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G18_10b_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G18_10c_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_NEUT562_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                      ]

        make_generator_comp(det+"_"+flux+"_"+targ+"_ehad_gencomp.pdf", inFileList, nameList, colzList, ehad, "100,0,2", ccinc, \
                            "E_{had} (GeV); d#sigma/dE_{had} (#times 10^{-38} cm^{2}/GeV/nucleon)")
                
        make_generator_comp(det+"_"+flux+"_"+targ+"_ehadoverq0_gencomp.pdf", inFileList, nameList, colzList, "("+ehad+")/q0", "124,0.79,1.1", ccinc +"&& ("+ehad+")!=0", \
                            "E_{had}^{rec}/q_{0}; d#sigma/d(E_{had}^{rec}/q_{0}) (#times 10^{-38} cm^{2}/nucleon)", [0.25, 0.5, 0.45, 0.93], [0, None], [0,2.2])

        
    ## Now T2K
    det   = "T2KND"
    targ  = "H2O"
    for flux in ["FHC_numu", "RHC_numubar"]:
        inFileList = [inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G18_10b_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G18_10c_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_NEUT562_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                      ]
        make_generator_comp(det+"_"+flux+"_"+targ+"_ehad_gencomp.pdf", inFileList, nameList, colzList, ehad, "100,0,1", cc0pi, \
                            "E_{had} (GeV); d#sigma/dE_{had} (#times 10^{-38} cm^{2}/GeV/nucleon)")

	make_generator_comp(det+"_"+flux+"_"+targ+"_ehadoverq0_gencomp.pdf", inFileList, nameList, colzList, "("+ehad+")/q0", "120,0,1.2", cc0pi, \
                            "E_{had}^{rec}/q_{0}; d#sigma/d(E_{had}^{rec}/q_{0}) (#times 10^{-38} cm^{2}/nucleon)", [0.25, 0.5, 0.45, 0.93], [0, None], [0,2.2])

        
        
if __name__ == "__main__":

    inputDir="/global/cfs/cdirs/dune/users/cwilk/MC_IOP_review/*/"
    make_q0_plots(inputDir)
    make_ehad_plots(inputDir)


    
