# Champions 


This project is still in development and has an experimental status. The Documentation is hosted at [champions-ab0723.gitlab.io](https://champions-ab0723.gitlab.io).



If you want to try this package out you can do it with the following commands:

```bash
git clone https://gitlab.com/gwhe/champions.git
cd champions
uv sync 
cd examples/mnist
download the file from  https://www.kaggle.com/datasets/oddrationale/mnist-in-csv
then open files dc_mninst.yaml and change test_files: and train_files: to the dowloaded 
chmod u+x run.sh
./run.sh 
--- trink some coffe (or espresso) --- 
if job is finished then look at the files at ./eval folder
```

of cource you can also install the package with pip (uv add champion). More infos can be found in the docu.