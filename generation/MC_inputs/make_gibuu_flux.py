import csv
import sys
import ROOT

def convert_flux_gibuu(input_file_name, input_hist_name, output_file_name):

    input_file = ROOT.TFile(input_file_name)
    input_hist = input_file.Get(input_hist_name)

    nbins  = input_hist.GetNbinsX()
    edges = [input_hist.GetXaxis().GetBinLowEdge(i+1) for i in range(nbins)]
    edges.append(input_hist.GetXaxis().GetBinUpEdge(nbins))
    bin_widths = [edges[i+1] - edges[i] for i in range(nbins)]
    finest_width = min(bin_widths)
    
    with open(output_file_name, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for i in range(nbins):

            bin_val = input_hist.GetBinContent(i + 1)
            start = edges[i]
            end = edges[i+1]
            n_sub_bins = int(round((end - start) / finest_width))

            for j in range(n_sub_bins):
                center = start + (j + 0.5) * finest_width
                writer.writerow(['%.6g' % center, bin_val])
    return

    
if __name__ == '__main__':

    if len(sys.argv) < 3:
        print("The input file name and input histogram name are required arguments!")
        sys.exit()

    input_file_name  = sys.argv[1]
    input_hist_name  = sys.argv[2]
    output_file_name = "gibuu_flux.dat"
    if len(sys.argv) == 4: output_file_name = sys.argv[3]

    print("Generating a GiBUU appropriate flux in", output_file_name, "from", input_file_name, ":", input_hist_name)
    convert_flux_gibuu(input_file_name, input_hist_name, output_file_name)
