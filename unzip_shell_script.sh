input_loc=$1
output_loc=$2

input_loc_list=`gsutil ls $input_loc`
output_loc_list=`gsutil ls $output_loc`

# echo $input_loc_list
for FILE in $input_loc_list; 
    do 
        file_name=`echo $FILE | cut -d/ -f6`
        echo "$output_loc$file_name"
        gsutil cat $FILE | unzip | gsutil cp - "$output_loc"
        echo $file " done"

done

# echo $output_loc_list