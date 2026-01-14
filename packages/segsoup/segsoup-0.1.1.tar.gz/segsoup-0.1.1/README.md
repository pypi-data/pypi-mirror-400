# SegSoup

Model soups were originally introduced in the paper [Model soups: averaging weights of multiple fine-tuned models improves accuracy without increasing inference time](https://arxiv.org/abs/2203.05482). As the title suggests, they can be created by averaging the weights of multiple models fine-tuned with different hyperparameter configurations. This technique has been shown to often improve accuracy and robustness for classification models without incurring any additional inference or memory costs.

**SegSoup** is a library that aims to facilitate the creation of model soups for semantic segmentation independently of the underlying architecture of the segmentation model. In this way, users can try to improve the performance of traditional CNN-based models or vision transformer models using this library. 

Furthermore, three "recipes" can be used for model souping:

- **Uniform soup**: The model soup is created by simply averaging the weights of all models.
- **Weighted soup**: Different weights can be assigned to each model. For example, when creating a soup from sequential checkpoints of the same training run, higher weights can be given to later and more fully trained checkpoints.
- **Greedy soup**: Models are sequentially added to the soup and kept only if the validation performance of the resulting soup improves.


