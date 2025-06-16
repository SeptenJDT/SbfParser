trap if_error ERR

function if_error {
  cd example
  echo "An error occurs."
}

clear
cd ..
python3 setup.py build
python3 setup.py build_ext --inplace
python3 setup.py install
cd example
