# Repository description
Current repository shows, how to deal with Machine Learning and AWS DeepLens edge device.
It is based on the example project provided by Amazon - [Amazon SageMaker Object Detection from Scratch](
https://github.com/aws-samples/amazon-sagemaker-object-detection-from-scratch).

The main goal of the repository is to give an introduction, how to prepare your own train data set with AWS DeepLens, 
train a model with SageMaker and avoid expenses caused by the usage of expensive AWS resources, like SageMaker Studio 
and AWS GroundTruth.
It's rather simple to forget to release resources or underestimate a price of labeling jobs - which may cause you lose
a few hundred dollars.
I assume, that you already set up your AWS account, registered DeepLens device, and played with example projects. So, I 
won't explain the basics.<br/>
<strong>In this example, I'm focusing on the most interesting part (imho) - collect and prepare training data. All examples, I 
saw, ignore this important step.</strong>

# Our goal
Let's make our AWS DeepLens to recognize banknotes. As an example, I used Russian Rubles.

## Steps
1. Collect a number of images, by capturing frames from AWS DeepLens. It makes a sense to use the same camera for
preparing and processing data.
2. Label prepared images. During the labeling job you will mark objects with bounding boxes.
3. Label shall be transformed to the applicable format, consumed by the model.
4. Train the model and deploy it on DeepLens device.

### Collect Images
The simplest way to do that, capture frames one by one from the <b>project stream</b>.<br/>
Deploy pretrained [model](model/patched_model.tar) and [lambda function](function/money-counter-function) to the 
device.
It's necessary to increase a 'detection_threshold' in the lambda function to avoid appearance of bounding boxes as we 
don't need them on training images.

[bash_scripts](bash_scripts) folder contains helpful scripts, that make work with a device more convenient.<br/>
Connect to your device using Micro HDMI cable and copy scripts folder.<br/>

Use 'capture_single_frame.sh' to save frames from device output (project stream) to the file system.
<strong>Script is not perfect, and sometimes it's necessary to repeat its execution several times because of artifacts 
on images.</strong><br/>
Basically, the more train images you do, the more precise will be predictions of you model.<br/>
Download images from your device to the local file system, when you're ready.<br/>
[dataset](dataset) folder contains my images, collected for both sides of two banknotes.

### Data Labeling
Amazon provides an AWS GroundTruth service for images labeling. It provides the result in a format, that can be
consumed by the training job without of any transformations. Unfortunately, it's pretty expensive and not very usable.
I recommend singing up to [Labelbox](https://app.labelbox.com), as it has a free trial version. And its result 
can be transformed using [resize_dataset_300x300.py](dataset/resize_dataset_300x300.py). This script runs locally,
resizes (not needed for this example) images, and creates a manifest file, that will be used for the training job.<br/>

The whole sequence looks as follows: 
- create a new project on Label box for <b>each</b> sub-set of images (1000_front, 1000_back, 2000_front, 2000_back), 
upload you images and complete labeling
- modify script using your data to download data from Labelbox (can be found in the 'Export' section of Label box's UI)
- execute script for each project and collect resulting data manually to the single manifest file. See: 
[sg-manifest.manifest](dataset/sg-manifest.manifest)<br/>
:information_source: More about manifest file format can be found 
[here](https://docs.aws.amazon.com/sagemaker/latest/dg/object-detection.html)

### Model Training
Instead of using SageMaker Studio, it's more reasonable to start experimenting in 
[SageMaker Studio Lab](https://studiolab.sagemaker.aws/). It's free of charge, and has all we need. Don't hesitate to
ask Amazon, to provide you an account.<br/>
- create and run new environment in 'SageMaker Studio Lab'
- upload [notebook](notebook/MoneyCounter.ipynb) and [incubator.tar.gz.part*](notebook)
- create new Terminal: File -> New -> Terminal
- join archive parts: cat incubator.tar.gz.parta* > incubator.tar.gz
- extract incubator: tar -xzf incubator.tar.gz
- run the notebook step by step. Read provided descriptions carefully and modify code if necessary!

### Deploy Trained Model to the Device
Update re-deploy you DeepLens project.<br/>
<strong>Don't forget to decrease the 'detection_threshold' value in your lambda function.</strong> Otherwise, you won' 
see any bounding boxes, because the 'confidence_score' will be always lower than the detection threshold. 

## Troubleshooting 
Useful information can be found in AWS article 
[Logging and Troubleshooting Your AWS DeepLens Project](https://docs.aws.amazon.com/deeplens/latest/dg/deeplens-logging-and-troubleshooting.html)
<br/>
:warning: Every time you change your Lambda function or re-train the model, don't forget to publish a new version of your 
function, re-import model, and update AWS DeepLens project before its re-deployment to the device.<br/>
:warning: Sometimes device demonstrates a weird behavior - you re-deployed the model, but it predicts the same way.<br/>
Try to back up your device folder '/opt/awscam/artifacts' and remove everything from it. Then re-deploy your project 
again.