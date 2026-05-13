import torch
from urllib.request import urlopen
from PIL import Image
from open_clip import create_model_from_pretrained, get_tokenizer

# Load the model and config files from the Hugging Face Hub

class ClassifierSingleton:
    def __init__(self):
        model, preprocess = create_model_from_pretrained('hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224')
        tokenizer = get_tokenizer('hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224')


    # Zero-shot image classification
    template = 'this is a photo of '
    labels = [
        'brain MRI',
        'covid line chart',
        'bone X-ray',
        'chest X-ray',
        'chest CT',
        'abdomen CT'
    ]


    test_imgs = [
        '1.jpg',
        # "img.png"
    ]
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    model.to(device)
    model.eval()

    context_length = 256

    images = torch.stack([preprocess(Image.open(img)) for img in test_imgs]).to(device)
    texts = tokenizer([template + l for l in labels], context_length=context_length).to(device)
    with torch.no_grad():
        image_features, text_features, logit_scale = model(images, texts)

        logits = (logit_scale * image_features @ text_features.t()).detach().softmax(dim=-1)
        sorted_indices = torch.argsort(logits, dim=-1, descending=True)

        logits = logits.cpu().numpy()
        sorted_indices = sorted_indices.cpu().numpy()

    top_k = -1

    for i, img in enumerate(test_imgs):
        pred = labels[sorted_indices[i][0]]

        top_k = len(labels) if top_k == -1 else top_k
        print(img.split('/')[-1] + ':')
        for j in range(top_k):
            jth_index = sorted_indices[i][j]
            print(f'{labels[jth_index]}: {logits[i][jth_index]}')
        print('\n')
