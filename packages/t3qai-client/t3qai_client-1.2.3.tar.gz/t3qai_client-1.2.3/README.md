# t3qai_client Description
a library for t3qai platform client.

The client module provides properties/functions
that links platform and client's learning/Inference algorithm.

- Provide platform path properties
- Provides functions to link learning state, set log, call learning parameter elements, load data, save learning results, and download inference results

## To install with pip
```
pip install t3qai_client

```

## How to Use (Example)
### properties
```
## train
from t3qai_client import T3QAI_TRAIN_OUTPUT_PATH, T3QAI_TRAIN_MODEL_PATH, T3QAI_TRAIN_DATA_PATH, T3QAI_MODULE_PATH

## inference
from t3qai_client import T3QAI_INIT_MODEL_PATH, T3QAI_MODULE_PATH
```

### functions
```
import t3qai_client as tc

## link learning state
tc.train_start()
tc.train_finish(result, result_msg)

## set log
# train
tc.train_set_logger()
# inference
tc.inference_set_logger()

## call learning parameter elements
# train
params = tc.train_load_param()
batch_size= int(params['batch_size'])
# inference
params = tc.inference_load_param()
batch_size= int(params['batch_size'])

## save learning results
# save the learning results inside the platform.
eval_results={}
eval_results['accuracy']=  0.93
eval_results['loss']=  0.003
tc.train_save_result_metrics(eval_results)

## To download inference results at platform (2 options -> file_obj or file_path)
from t3qai_client import DownloadFile
result = DownloadFile(file_obj=resultobj, file_name=filename)
result = DownloadFile(file_path=save_path, file_name=filename)
```