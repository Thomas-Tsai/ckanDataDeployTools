# ckanDataDeployTools

## ckanSync

## usage

python ckanSync.py <dataset>
    
    (dev_env) thomas@localhost:~/ckanDataDeployTools$ python ckanSync.py mnist
    29cb3660-c770-419c-8768-deb060bd7f6d :  mnist
    mnist :  train-labels-idx1-ubyte.gz :  https://aidm.nchc.org.tw/dataset/.../download/train-labels-idx1-ubyte.gz
    mnist :  t10k-images-idx3-ubyte.gz :  https://aidm.nchc.org.tw/dataset/.../download/t10k-images-idx3-ubyte.gz
    mnist :  t10k-labels-idx1-ubyte.gz :  https://aidm.nchc.org.tw/dataset/.../download/t10k-labels-idx1-ubyte.gz
    mnist :  train-images-idx3-ubyte.gz :  https://aidm.nchc.org.tw/dataset/.../download/train-images-idx3-ubyte.gz
    (dev_env) thomas@localhost:~/ckanDataDeployTools$ tree datasets/
    datasets/
    └── mnist
        ├── t10k-images-idx3-ubyte.gz
        ├── t10k-labels-idx1-ubyte.gz
        ├── train-images-idx3-ubyte.gz
        └── train-labels-idx1-ubyte.gz

    1 directory, 4 files

## example of ckan.ini

remember to replace key!

    [site]
    url=https://aidm.nchc.org.tw
    key=<<your ckan api key>>
    [dataset]
    group=ai
    [local]
    data_root_directory=./datasets
    sync=true
    logfile=sync.log
    statusfile=status.log
    metafile=sync.meta
    debug=0

