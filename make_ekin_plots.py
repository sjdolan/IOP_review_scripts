import ROOT
from ROOT import gStyle, TGaxis, TPad, TLine, gROOT, TH1, TColor, TCanvas, TFile, TH1D, gPad, TLegend, kWhite, gDirectory
from glob import glob

from plotting_functions import make_generator_comp

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

def make_DUNE_Ekin_plots(inputDir="inputs/"):

    nameList = ["GENIE 10a",\
                "GENIE 10b",\
                "GENIE 10c",\
                "CRPA",\
                "SuSAv2",\
                "NEUT",\
                "NuWro"\
                ]
    colzList = [9000, 9001, 9002, 9003, 9004, 9006, 9005]
    
    ## Ekin cut
    ekin = "E - sqrt(E*E - px*px - py*py - pz*pz)"

    mom = "sqrt(px*px - py*py - pz*pz)"
    
    ## Loop over configs
    for det in ["DUNEND", "T2KND"]: #"DUNEFD_osc"]:

        targ = "Ar40"
        if det == "T2KND": targ="H2O"
        
        for flux in ["FHC_numu", "RHC_numubar"]:
            
            for pdg in [2212, -211, 211]: #211, -211, 13, -13, 2212, 11, -11, 111, 22, 321, -321, 311]:
                
                pdg_cut = "pdg=="+str(pdg)
                
                ## K0 is a special case
                if pdg == 311: pdg_cut = "(pdg==311|pdg==130|pdg==310)"
                
                ## These files can be found here (no login required): https://portal.nersc.gov/project/dune/data/2x2/simulation
                inFileList = [inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                              inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G18_10b_00_000_1M_*_NUISFLAT.root",\
                              inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G18_10c_00_000_1M_*_NUISFLAT.root",\
                              inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                              inputDir+"/"+det+"_"+flux+"_"+targ+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                              inputDir+"/"+det+"_"+flux+"_"+targ+"_NEUT562_1M_*_NUISFLAT.root",\
                              inputDir+"/"+det+"_"+flux+"_"+targ+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                              ]
                
                make_generator_comp(det+"_"+flux+"_"+targ+"_"+str(pdg)+"_mom_gencomp.png", inFileList, nameList, colzList, mom, "100,0,1", pdg_cut, \
                                    "p (GeV/c); d#sigma/dp (#times 10^{-38} cm^{2}/nucleon)")
                
            
            
if __name__ == "__main__":

    inputDir="/global/cfs/cdirs/dune/users/cwilk/MC_IOP_review/*/"
    make_DUNE_Ekin_plots(inputDir)

#  LocalWords:  numubar
