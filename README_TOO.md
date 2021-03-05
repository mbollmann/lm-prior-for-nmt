Notes on how to _actually_ get this to run:

- Install PyTorch through conda (`conda install pytorch==1.4.0`), as this
  version is no longer on PyPi and the newest one (1.8.0) doesn't work out of
  the box
- The previous step might downgrade your Python version in your conda
  environment, so make sure to do the following steps _afterwards_.
- Install other requirements, _but_ due to dependency issues, install `scipy`
  separately first.  Also installing `fasttext` through pip didn't work for me,
  I cloned the repo and followed the instructions here:
  https://fasttext.cc/docs/en/support.html
- `tensorboard` is missing from the requirements; `tokenizers` is needed by my
  own changes
