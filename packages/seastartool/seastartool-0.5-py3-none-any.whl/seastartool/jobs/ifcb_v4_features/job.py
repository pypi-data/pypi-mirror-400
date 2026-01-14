import planktofeatures.extractors
import os
import libifcb
import time
import csv

class MainJob:
    def __init__(self, options, progress_reporting_function = lambda prop, etr : print(str(int(prop*10000)/100) + "% done - ETR " + str(int(etr)) + "s"), log_function = lambda txt : print("[LOG] " + txt), error_function = lambda txt : print("[ERR] " + txt)):
        self.options = options
        self.report_progress = progress_reporting_function
        self.log_function = log_function
        self.error_function = error_function

        input_files_list = []
        for input_file_path in options["input_files"]:
            input_files_list.append(os.path.realpath(input_file_path))

        ifcb_bins = []
        ifcb_files = []
        roi_readers = []

        intermediate_files_list = set()
        for file_name in input_files_list:
            intermediate_files_list.add(os.path.splitext(file_name)[0])

        for file_name in intermediate_files_list:
            ifcb_bins.append(os.path.basename(file_name))
            ifcb_files.append(file_name)


        self.log_function("Creating ROIReaders")

        for i in range(len(ifcb_files)):
            self.log_function("Loading \"" + ifcb_files[i] + ".hdr\"")
            roi_readers.append(libifcb.ROIReader(ifcb_files[i] + ".hdr", ifcb_files[i] + ".adc", ifcb_files[i] + ".roi"))

        self.roi_readers = roi_readers
        self.ifcb_files = ifcb_files
        self.ifcb_bins = ifcb_bins
        self.total_rois = 0
        for roi_reader in roi_readers:
            self.total_rois += len(roi_reader.rows)

    def generate_features_one_file(self, sample, source_file, bin_id, csv_file):
        self.log_function("Processing \"" + source_file + ".roi\"")
        first = True
        feature_extractor = planktofeatures.extractors.WHOIVersion4()
        with open(csv_file, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)
            adc_row_idx = 0
            total_rows = len(sample.rows)
            for adc_row_obj in sample.rows:
                adc_row_idx += 1
                self.currently_processing += 1
                img = adc_row_obj.image
                if img is not None:
                    feature_object = feature_extractor.process(img)
                    row_features = feature_object.values
                    observation_id = bin_id + "_" + str(adc_row_obj.index).zfill(5)
                    if first:
                        first = False
                        akeys = list(map(str.lower,row_features.keys()))
                        csv_writer.writerow(["roi_number", "roi_id", "feature_extractor", *akeys])
                    csv_writer.writerow([adc_row_idx, observation_id,"whoi_v4", *row_features.values()])

                if adc_row_idx % 16 == 0:
                    self.last_time = time.time()
                    proportion = self.currently_processing/self.total_rois
                    elapsed_time = self.last_time - self.first_time
                    time_per_roi = elapsed_time / self.currently_processing
                    remaining_rois = self.total_rois - self.currently_processing
                    remaining_time = time_per_roi * remaining_rois
                    self.report_progress(proportion, remaining_time) # Placeholdr

    def execute(self):
        self.first_time = time.time()
        self.currently_processing = 0
        self.last_time = time.time()
        for roi_reader_idx in range(len(self.roi_readers)):
            csv_file = os.path.join(self.options["output_folder"], self.ifcb_bins[roi_reader_idx] + "_features_v4.csv")
            self.generate_features_one_file(self.roi_readers[roi_reader_idx], self.ifcb_files[roi_reader_idx], self.ifcb_bins[roi_reader_idx], csv_file)
