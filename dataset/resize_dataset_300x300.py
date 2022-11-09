print('Resize images to 300x300. Transform manifest file...')


def download_labelbox(src_images_folder, sage_maker_manifest_file_name, bucket, annotations_title_to_id):
    print('Download Labelbox data...')
    import labelbox
    import numpy as np
    import json
    import boto3
    import os

    s3 = boto3.resource('s3')

    # Enter your Labelbox API key here
    LB_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...6-NEnL2xets"

    # Create Labelbox client
    lb = labelbox.Client(LB_API_KEY, "https://api.labelbox.com/graphql")
    # Get project by ID
    project = lb.get_project('cl9...6chy')
    # Export image and text data as an annotation generator:
    #labels = project.label_generator()
    # Export video annotations as an annotation generator:
    #labels = project.video_label_generator()
    # Export labels created in the selected date range as a json file:
    labels = project.export_labels(download = True, start="2022-10-24", end="2022-10-30")
    data = np.array(labels)
    with open(src_images_folder + '/' + sage_maker_manifest_file_name, mode='w') as manifest:
        for item in data:
            if item:
                image_file_name = item['External ID']
                annotations = []
                sg_item = {"source-ref": "s3://{}/input/{}/{}".format(bucket, src_images_folder, image_file_name),
                           "cash": {"image_size": [{"width": 300, "height": 300, "depth": 3}],
                                    "annotations": annotations}}
                # print('Item: ', sg_item)
                for labeledObject in item['Label']['objects']:
                    bounding_box = labeledObject['bbox']
                    annotation = {"class_id": annotations_title_to_id[labeledObject['title']],
                                  "top": bounding_box['top'], "left": bounding_box['left'],
                                  "height": bounding_box['height'], "width": bounding_box['width']}
                    annotations.append(annotation)

                manifest.write(json.dumps(sg_item) + os.linesep)


def resize(src_images_folder='2000_front', sage_maker_manifest_file_name='sg-manifest.manifest', new_size=300,
           bucket='deeplens-money-counter-data', annotations_title_to_id={'2000': 0}):

    import json, os, rglob
    from PIL import Image

    download_labelbox(src_images_folder, sage_maker_manifest_file_name, bucket, annotations_title_to_id)
    print('Transform manifest...')
    target_images_folder = src_images_folder + '-{}x{}'.format(new_size, new_size)
    if not os.path.isdir(target_images_folder):
        os.mkdir(target_images_folder)

    with open(os.path.join(target_images_folder, sage_maker_manifest_file_name),
              mode='w') as target_manifest:
        with open(os.path.join(src_images_folder, sage_maker_manifest_file_name), mode='r') as source_manifest:
            for item in source_manifest:
                item_json = json.loads(item)
                scale = item_json['cash']['image_size'][0]['width'] / new_size
                item_json['cash']['image_size'][0]['width'] = item_json['cash']['image_size'][0]['height'] = new_size
                for annotation in item_json['cash']['annotations']:
                    annotation['top'] = int(annotation['top'] / scale)
                    annotation['left'] = int(annotation['left'] / scale)
                    annotation['height'] = int(annotation['height'] / scale)
                    annotation['width'] = int(annotation['width'] / scale)

                target_manifest.write(json.dumps(item_json) + os.linesep)

    target_manifest.close()

    print('Resize images...')

    jpeg_files = rglob.rglob(src_images_folder, "*.jpeg")
    for jpeg_file in jpeg_files:
        Image.open(jpeg_file).resize((new_size, new_size)).save(os.path.join(target_images_folder,
                                                                             jpeg_file.split('/')[-1]))


resize(bucket='deeplens-money-counter-data', src_images_folder='1000_front',
       sage_maker_manifest_file_name='sg-manifest.manifest', new_size=300, annotations_title_to_id={'1000': 0})


