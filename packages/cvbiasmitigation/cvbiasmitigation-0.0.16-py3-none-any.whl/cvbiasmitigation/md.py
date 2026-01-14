def get_flac_markdown():
    md = """
### How to employ FLAC
#### First install the flacloss library
```
pip install flacloss
```
#### Train a bias capturing classifier 
In this step you should get a model that is trained to predict the sensitive attribute. You can either use a pretrained model (e.g., [here](https://github.com/gsarridis/FLAC/releases/tag/bcc) you can find classifiers for gender, age, and race) or train your own model by running the following code
```
def train(trainloader, net, epochs):
    lossfunc = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
    net.train()
    for epoch in range(epochs):
        for inputs, labels, sensitive in trainloader:
            optimizer.zero_grad()
            inputs, labels, sensitive = inputs.to(device), labels.to(device), sensitive.to(device)
            outputs, features = net(inputs)
            # Here use "sensitive" as target
            loss = lossfunc(outputs, sensitive)
            loss.backward()
            optimizer.step()
```
#### Train the fair model
Now use the bias capturing classifier (bcc) from the previous step and the flac loss to mitigate the bias.
```
def flac_train(trainloader, net, bcc, epochs, weight=100):
    lossfunc = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
    bcc.eval()
    net.train()
    for epoch in range(epochs):
        for inputs, labels, sensitive in trainloader:
            optimizer.zero_grad()
            inputs, labels, sensitive = inputs.to(device), labels.to(device), sensitive.to(device)
            outputs, features = net(inputs)
            loss = lossfunc(outputs, labels)
            with torch.no_grad():
                _, sensfeats = bcc(inputs)
            loss += weight*flac.flac_loss(sensfeats, features, torch.squeeze(labels))
            loss.backward()
            optimizer.step()
```
"""

    return md


def get_badd_markdown():
    md = """
### How to employ BAdd

#### First get a bias capturing classifier 
In this step you should get a model that is trained to predict the sensitive attribute. 
Here there are three options:
1. You can use a pretrained model (e.g., [here](https://github.com/gsarridis/FLAC/releases/tag/bcc) you can find classifiers for gender, age, and race) 
2. You can train your own model by running the following code
```
def train(trainloader, net, epochs):
    lossfunc = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
    net.train()
    for epoch in range(epochs):
        for inputs, labels, sensitive in trainloader:
            optimizer.zero_grad()
            inputs, labels, sensitive = inputs.to(device), labels.to(device), sensitive.to(device)
            outputs, features = net(inputs)
            # Here use "sensitive" as target
            loss = lossfunc(outputs, sensitive)
            loss.backward()
            optimizer.step()
```
3. You can just encode the sensitive labels so that the have the same size as your main model
```
num_classes = 2 # Set the number of classes of the sensitive attribute
sensitive_net = nn.Linear(10,512)
sensitive_net.to(device)
```
In general, 3rd option is the easiest one to be applied.
#### Add a badd-based forward function to your model class
```
The only difference between this and the typical forward function is that we add the sensitive features to the main features prior to the classification layer.
def badd_forward(self, x, sens_feat):
    # copy paste from forward function all the layers and add the sensitive features prior to the classification layer. 
    # for a typical resnet this would be as follows
    x = self.conv1(x)
    x = self.bn1(x)
    x = self.relu(x)
    x = self.maxpool(x)

    x = self.layer1(x)
    x = self.layer2(x)
    x = self.layer3(x)
    x = self.layer4(x)

    x = self.avgpool(x)
    x = torch.flatten(x, 1)

    # Here add the sensitive features
    x += sens_features

    x = self.fc(x)
    return x
```
#### Train the fair model
```
def train(trainloader, net, sensitive_net, epochs):
    lossfunc = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
    net.train()
    sensitive_net.eval()
    for epoch in range(epochs):
        for inputs, labels, sensitive in trainloader:
            optimizer.zero_grad()
            inputs, labels, sensitive = inputs.to(device), labels.to(device), sensitive.to(device)
            with torch.no_grad():
                # for bcc 3rd option 
                sensitive = F.one_hot(sensitive, num_classes=num_classes).float()
                sens_feat = sensitive_net(sensitive)
                # for bcc 1st and 2nd option 
                _, sens_feat = sensitive_net(sensitive)
            outputs = model.badd_forward(inputs,sens_feat)
            loss = lossfunc(outputs, labels)
            loss.backward()
            optimizer.step()
```
"""

    return md


def get_adaface_markdown():
    md = """
### How to run AdaFace

#### Installation

First, clone the official github repository of Adaface
```
git clone https://github.com/mk-minchul/AdaFace.git
```

Then create a virtual environment
```
conda create --name adaface pytorch==1.8.0 torchvision==0.9.0 cudatoolkit=10.2 -c pytorch
conda activate adaface
conda install scikit-image matplotlib pandas scikit-learn 
pip install -r requirements.txt
```

#### Data Preparation

##### Using InsightFace Dataset


InsightFace provides a variety of labeled face dataset preprocessed to 112x112 size. 

[insightface link](https://github.com/deepinsight/insightface/tree/master/recognition/_datasets_)

The unzipped dataset looks as follows
```
example: faces_webface_112x112
└── train.rec   
├── train.idx                                                                                       │
├── train.lst                                                                                       │
├── agedb_30.bin                                                                                    │
├── calfw.bin                                                                                       │
├── cfp_ff.bin                                                                                      │
├── cfp_fp.bin                                                                                      │
├── cplfw.bin                                                                                       │
├── lfw.bin                                                                                         │
```

`train.rec` contains all the training dataset images and `rec` format combines all data to a single file 
whilst allowing indexed access. 
`rec` file is good when one does not one to create millions of individual image files in storage. 

We provide a training code that utilizes this `rec` file directly without converting to `jpg` format. 
But if one ones to convert to `jpg` images and train, refer to the next section. 

1. Download the dataset from [insightface link](https://github.com/deepinsight/insightface/tree/master/recognition/_datasets_)
2. Unzip it to a desired location, `DATASET_ROOT`  _ex)_ `/data/`. 
3. The result folder we will call `DATASET_NAME`, ex) `faces_webface_112x112`.
4. For preprocessing run
   1. `python convert.py --rec_path <DATASET_ROOT>/<DATASET_NAME> --make_validation_memfiles`
5. During training, 
   1. turn on the option `--use_mxrecord` 
   2. set `--data_root` equal to `DATASET_ROOT`
   3. set `--train_data_path` to the `DATASET_NAME`.
   4. set `--val_data_path` to the `DATASET_NAME`.

* Note you cannot turn on `--train_data_subset` option. For this you must expand the dataset to images 
(refer to below section).

##### Using Image Folder Dataset

Another option is to extract out all images from the InsightFace train.rec file. 
It uses the directory as label structure, and you can swap it with your own dataset. 

1. Download the dataset from [insightface link](https://github.com/deepinsight/insightface/tree/master/recognition/_datasets_)
2. Unzip it to a desired location, `DATASET_ROOT`  _ex)_ `/data/`.
3. The result folder we will call `DATASET_NAME`, ex) `faces_webface_112x112`.
4. For preprocessing run
   1. `python convert.py --rec_path <DATASET_ROOT>/<DATASET_NAME> --make_image_files --make_validation_memfiles`
5. During training,
   1. **do not** turn on the option `--use_mxrecord`
   2. Rest are the same.
   3. set `--data_root` equal to `DATASET_ROOT`
   4. set `--train_data_path` to the `DATASET_NAME`.
   5. set `--val_data_path` to the `DATASET_NAME`.

##### Custom Dataset

If you want to use your custom training dataset, prepare images in folder (as label) structure 
and change the `--data_root` and `--train_data_path` accordingly. The custom dataset should be located at `<data_root>/<train_data_path>`


#### Train 
- Sample run scripts are provided in `scripts`
- EX) Run `bash script/run_ir50_ms1mv2.sh` after changing the `--data_root` and `--train_data_path` to fit your needs. 
- If you are using ImageFolder dataset, then remove `--use_mxrecord`.
* [IMPORTANT] Once the training script has started, check if your image color channel is correct by looking at the sample stored in `<RUN_DIR>/training_samples`. 

"""

    return md


def get_flac_json():
    json = [
        {"type": "heading", "level": 3, "content": "How to employ FLAC"},
        {
            "type": "heading",
            "level": 4,
            "content": "First install the flacloss library",
        },
        {"type": "code", "language": "bash", "content": "pip install flacloss"},
        {"type": "heading", "level": 4, "content": "Train a bias capturing classifier"},
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "content": "In this step you should get a model that is trained to predict the sensitive attribute. You can either use a pretrained model (e.g., ",
                },
                {
                    "type": "link",
                    "url": "https://github.com/gsarridis/FLAC/releases/tag/bcc",
                    "content": "here",
                },
                {
                    "type": "text",
                    "content": " you can find classifiers for gender, age, and race) or train your own model by running the following code:",
                },
            ],
        },
        {
            "type": "code",
            "language": "python",
            "content": 'def train(trainloader, net, epochs):\n    lossfunc = nn.CrossEntropyLoss()\n    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)\n    net.train()\n    for epoch in range(epochs):\n        for inputs, labels, sensitive in trainloader:\n            optimizer.zero_grad()\n            inputs, labels, sensitive = inputs.to(device), labels.to(device), sensitive.to(device)\n            outputs, features = net(inputs)\n            # Here use "sensitive" as target\n            loss = lossfunc(outputs, sensitive)\n            loss.backward()\n            optimizer.step()',
        },
        {"type": "heading", "level": 4, "content": "Train the fair model"},
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "content": "Now use the bias capturing classifier (bcc) from the previous step and the flac loss to mitigate the bias.",
                }
            ],
        },
        {
            "type": "code",
            "language": "python",
            "content": "def flac_train(trainloader, net, bcc, epochs, weight=100):\n    lossfunc = nn.CrossEntropyLoss()\n    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)\n    bcc.eval()\n    net.train()\n    for epoch in range(epochs):\n        for inputs, labels, sensitive in trainloader:\n            optimizer.zero_grad()\n            inputs, labels, sensitive = inputs.to(device), labels.to(device), sensitive.to(device)\n            outputs, features = net(inputs)\n            loss = lossfunc(outputs, labels)\n            with torch.no_grad():\n                _, sensfeats = bcc(inputs)\n            loss += weight*flac.flac_loss(sensfeats, features, torch.squeeze(labels))\n            loss.backward()\n            optimizer.step()",
        },
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "content": "Note that FLAC is supported by the ",
                },
                {
                    "type": "link",
                    "url": "https://github.com/mever-team/vb-mitigator",
                    "content": "VB-Mitigator",
                },
                {
                    "type": "text",
                    "content": ", a code-base facilitating employing state-of-the-art visual bias mitigation algorithms.",
                },
            ],
        },
    ]

    return json


def get_badd_json():
    json = [
        {"type": "heading", "level": 3, "content": "How to employ BAdd"},
        {
            "type": "heading",
            "level": 4,
            "content": "First get a bias capturing classifier",
        },
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "content": "In this step you should get a model that is trained to predict the sensitive attribute. Here there are three options:",
                }
            ],
        },
        {
            "type": "list",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "You can use a pretrained model (e.g., ",
                        },
                        {
                            "type": "link",
                            "url": "https://github.com/gsarridis/FLAC/releases/tag/bcc",
                            "content": "here",
                        },
                        {
                            "type": "text",
                            "content": " you can find classifiers for gender, age, and race).",
                        },
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "You can train your own model by running the following code:",
                        },
                        {
                            "type": "code",
                            "language": "python",
                            "content": 'def train(trainloader, net, epochs):\n    lossfunc = nn.CrossEntropyLoss()\n    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)\n    net.train()\n    for epoch in range(epochs):\n        for inputs, labels, sensitive in trainloader:\n            optimizer.zero_grad()\n            inputs, labels, sensitive = inputs.to(device), labels.to(device), sensitive.to(device)\n            outputs, features = net(inputs)\n            # Here use "sensitive" as target\n            loss = lossfunc(outputs, sensitive)\n            loss.backward()\n            optimizer.step()',
                        },
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "You can just encode the sensitive labels so that they have the same size as your main model:",
                        },
                        {
                            "type": "code",
                            "language": "python",
                            "content": "num_classes = 2 # Set the number of classes of the sensitive attribute\nsensitive_net = nn.Linear(10,512)\nsensitive_net.to(device)",
                        },
                    ],
                },
            ],
        },
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "content": "In general, the third option is the easiest one to apply.",
                }
            ],
        },
        {
            "type": "heading",
            "level": 4,
            "content": "Add a BAdd-based forward function to your model class",
        },
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "content": "The only difference between this and the typical forward function is that we add the sensitive features to the main features prior to the classification layer.",
                }
            ],
        },
        {
            "type": "code",
            "language": "python",
            "content": "def badd_forward(self, x, sens_feat):\n    # Copy paste from forward function all the layers and add the sensitive features prior to the classification layer. \n    # For a typical ResNet this would be as follows:\n    x = self.conv1(x)\n    x = self.bn1(x)\n    x = self.relu(x)\n    x = self.maxpool(x)\n\n    x = self.layer1(x)\n    x = self.layer2(x)\n    x = self.layer3(x)\n    x = self.layer4(x)\n\n    x = self.avgpool(x)\n    x = torch.flatten(x, 1)\n\n    # Here add the sensitive features\n    x += sens_features\n\n    x = self.fc(x)\n    return x",
        },
        {"type": "heading", "level": 4, "content": "Train the fair model"},
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "content": "Use the following function for running the training procedure.",
                }
            ],
        },
        {
            "type": "code",
            "language": "python",
            "content": "def train(trainloader, net, sensitive_net, epochs):\n    lossfunc = nn.CrossEntropyLoss()\n    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)\n    net.train()\n    sensitive_net.eval()\n    for epoch in range(epochs):\n        for inputs, labels, sensitive in trainloader:\n            optimizer.zero_grad()\n            inputs, labels, sensitive = inputs.to(device), labels.to(device), sensitive.to(device)\n            with torch.no_grad():\n                # For BCC third option \n                sensitive = F.one_hot(sensitive, num_classes=num_classes).float()\n                sens_feat = sensitive_net(sensitive)\n                # For BCC first and second options \n                _, sens_feat = sensitive_net(sensitive)\n            outputs = model.badd_forward(inputs, sens_feat)\n            loss = lossfunc(outputs, labels)\n            loss.backward()\n            optimizer.step()",
        },
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "content": "Note that BAdd is supported by the ",
                },
                {
                    "type": "link",
                    "url": "https://github.com/mever-team/vb-mitigator",
                    "content": "VB-Mitigator",
                },
                {
                    "type": "text",
                    "content": ", a code-base facilitating employing state-of-the-art visual bias mitigation algorithms.",
                },
            ],
        },
    ]
    return json


def get_adaface_json():
    json = [
        {"type": "heading", "level": 3, "content": "How to run AdaFace"},
        {"type": "heading", "level": 4, "content": "Installation"},
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "content": "First, clone the official github repository of AdaFace.",
                }
            ],
        },
        {
            "type": "code",
            "language": "bash",
            "content": "git clone https://github.com/mk-minchul/AdaFace.git",
        },
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "content": "Then create a virtual environment."}
            ],
        },
        {
            "type": "code",
            "language": "bash",
            "content": "conda create --name adaface pytorch==1.8.0 torchvision==0.9.0 cudatoolkit=10.2 -c pytorch\nconda activate adaface\nconda install scikit-image matplotlib pandas scikit-learn \npip install -r requirements.txt",
        },
        {"type": "heading", "level": 4, "content": "Data Preparation"},
        {"type": "heading", "level": 5, "content": "Using InsightFace Dataset"},
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "link",
                    "url": "https://github.com/deepinsight/insightface/tree/master/recognition/_datasets_",
                    "content": "Insightface",
                },
                {
                    "type": "text",
                    "content": " provides a variety of labeled face datasets preprocessed to ",
                },
                {"type": "inline_code", "content": "112x112"},
                {"type": "text", "content": " size."},
            ],
        },
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "content": "The unzipped dataset looks as follows:"}
            ],
        },
        {
            "type": "code",
            "language": "bash",
            "content": "example: faces_webface_112x112\n└── train.rec   \n├── train.idx\n├── train.lst\n├── agedb_30.bin\n├── calfw.bin\n├── cfp_ff.bin\n├── cfp_fp.bin\n├── cplfw.bin\n├── lfw.bin",
        },
        {
            "type": "paragraph",
            "content": [
                {"type": "inline_code", "content": "train.rec"},
                {
                    "type": "text",
                    "content": " contains all the training dataset images, and the ",
                },
                {"type": "inline_code", "content": "rec"},
                {
                    "type": "text",
                    "content": " format combines all data into a single file while allowing indexed access. The ",
                },
                {"type": "inline_code", "content": "rec"},
                {
                    "type": "text",
                    "content": " format is useful when avoiding millions of individual image files in storage.",
                },
            ],
        },
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "content": "We provide training code that utilizes this ",
                },
                {"type": "inline_code", "content": "rec"},
                {"type": "text", "content": " file directly without converting to "},
                {"type": "inline_code", "content": "jpg"},
                {"type": "text", "content": " format. If you want to convert to "},
                {"type": "inline_code", "content": "jpg"},
                {
                    "type": "text",
                    "content": " images and train, refer to the next section.",
                },
            ],
        },
        {
            "type": "list",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "content": "Download the dataset from "},
                        {
                            "type": "link",
                            "url": "https://github.com/deepinsight/insightface/tree/master/recognition/_datasets_",
                            "content": "insightface",
                        },
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "content": "Unzip it to a desired location, "},
                        {"type": "inline_code", "content": "DATASET_ROOT"},
                        {"type": "text", "content": " (e.g., "},
                        {"type": "inline_code", "content": "/data/"},
                        {"type": "text", "content": ")."},
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "The result folder will be called ",
                        },
                        {"type": "inline_code", "content": "DATASET_NAME"},
                        {"type": "text", "content": ", e.g., "},
                        {"type": "inline_code", "content": "faces_webface_112x112"},
                        {"type": "text", "content": "."},
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "For preprocessing run: ",
                        },
                        {
                            "type": "inline_code",
                            "content": "python convert.py --rec_path <DATASET_ROOT>/<DATASET_NAME> --make_validation_memfiles",
                        },
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "During training, (i) turn on the option ",
                        },
                        {"type": "inline_code", "content": "--use_mxrecord"},
                        {
                            "type": "text",
                            "content": ", (ii) set ",
                        },
                        {"type": "inline_code", "content": "--data_root"},
                        {
                            "type": "text",
                            "content": " equal to ",
                        },
                        {"type": "inline_code", "content": "DATASET_ROOT"},
                        {
                            "type": "text",
                            "content": ", (ii) set ",
                        },
                        {"type": "inline_code", "content": "--train_data_path"},
                        {
                            "type": "text",
                            "content": " equal to ",
                        },
                        {"type": "inline_code", "content": "DATASET_NAME"},
                        {
                            "type": "text",
                            "content": ", (iv) set ",
                        },
                        {"type": "inline_code", "content": "--val_data_path"},
                        {
                            "type": "text",
                            "content": " equal to ",
                        },
                        {"type": "inline_code", "content": "DATASET_NAME"},
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "Note you cannot turn on ",
                        },
                        {
                            "type": "inline_code",
                            "content": "--train_data_subset",
                        },
                        {
                            "type": "text",
                            "content": " option. For this you must expand the dataset to images.",
                        },
                    ],
                },
            ],
        },
        {"type": "heading", "level": 5, "content": "Using Image Folder Dataset"},
        {
            "type": "list",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "content": "Download the dataset from "},
                        {
                            "type": "link",
                            "url": "https://github.com/deepinsight/insightface/tree/master/recognition/_datasets_",
                            "content": "insightface",
                        },
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "content": "Unzip it to a desired location, "},
                        {"type": "inline_code", "content": "DATASET_ROOT"},
                        {"type": "text", "content": " (e.g., "},
                        {"type": "inline_code", "content": "/data/"},
                        {"type": "text", "content": ")."},
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "The result folder will be called ",
                        },
                        {"type": "inline_code", "content": "DATASET_NAME"},
                        {"type": "text", "content": ", e.g., "},
                        {"type": "inline_code", "content": "faces_webface_112x112"},
                        {"type": "text", "content": "."},
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "For preprocessing run: ",
                        },
                        {
                            "type": "inline_code",
                            "content": "python convert.py --rec_path <DATASET_ROOT>/<DATASET_NAME> --make_validation_memfiles",
                        },
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "During training, (i) DO NOT turn on the option ",
                        },
                        {"type": "inline_code", "content": "--use_mxrecord"},
                        {
                            "type": "text",
                            "content": ", (ii) set ",
                        },
                        {"type": "inline_code", "content": "--data_root"},
                        {
                            "type": "text",
                            "content": " equal to ",
                        },
                        {"type": "inline_code", "content": "DATASET_ROOT"},
                        {
                            "type": "text",
                            "content": ", (ii) set ",
                        },
                        {"type": "inline_code", "content": "--train_data_path"},
                        {
                            "type": "text",
                            "content": " equal to ",
                        },
                        {"type": "inline_code", "content": "DATASET_NAME"},
                        {
                            "type": "text",
                            "content": ", (iv) set ",
                        },
                        {"type": "inline_code", "content": "--val_data_path"},
                        {
                            "type": "text",
                            "content": " equal to ",
                        },
                        {"type": "inline_code", "content": "DATASET_NAME"},
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "Note you cannot turn on ",
                        },
                        {
                            "type": "inline_code",
                            "content": "--train_data_subset",
                        },
                        {
                            "type": "text",
                            "content": " option. For this you must expand the dataset to images.",
                        },
                    ],
                },
            ],
        },
        {"type": "heading", "level": 5, "content": "Custom Dataset"},
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "content": "If you want to use your custom training dataset, prepare images in folder (as label) structure and change the ",
                },
                {"type": "inline_code", "content": "--data_root"},
                {"type": "text", "content": " and "},
                {"type": "inline_code", "content": "--train_data_path"},
                {
                    "type": "text",
                    "content": " accordingly. The custom dataset should be located at ",
                },
                {"type": "inline_code", "content": "<data_root>/<train_data_path>"},
                {"type": "text", "content": "."},
            ],
        },
        {"type": "heading", "level": 4, "content": "Train"},
        {
            "type": "list",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "\n \n - Sample run scripts are provided in ",
                        },
                        {"type": "inline_code", "content": "scripts"},
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "content": "\n - Example: Run "},
                        {
                            "type": "inline_code",
                            "content": "bash script/run_ir50_ms1mv2.sh",
                        },
                        {"type": "text", "content": " after changing the "},
                        {"type": "inline_code", "content": "--data_root"},
                        {"type": "text", "content": " and "},
                        {"type": "inline_code", "content": "--train_data_path"},
                        {"type": "text", "content": " to fit your needs."},
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "\n - If you are using an ImageFolder dataset, then remove ",
                        },
                        {"type": "inline_code", "content": "--use_mxrecord"},
                        {"type": "text", "content": "."},
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "content": "\n - [IMPORTANT] Once the training script has started, check if your image color channel is correct by looking at the sample stored in ",
                        },
                        {
                            "type": "inline_code",
                            "content": "<RUN_DIR>/training_samples",
                        },
                        {"type": "text", "content": "."},
                    ],
                },
            ],
        },
    ]
    return json
