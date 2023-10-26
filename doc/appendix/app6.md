---
title: 付録6 Evolution Gym のインストールに失敗したら?
date: 2023-10-20T07:41:03+0900
lastmod: 2023-10-20T07:41:03+0900
---

# 付録6 `Evolution Gym`のインストールに失敗したら?

`Evolution Gym`のインストールは、環境によってはうまくいかないことがあります。実際に、筆者は本家()のレポジトリからインストールしようとして最初は失敗しています。ここでは、`macOS`に`Evolution Gym`をインストールする手順と、遭遇する可能性がありそうな問題とその対応策をまとめてみました。インストールがうまくいかない場合は参考にしてみてください。

## `macOS`へのインストール手順

`macOS`へ`Evolution Gym`をインストールする手順はいくつかありますが、ここでは、本家のリポジトリをフォークして、必要な修正を施したリポジトリの`develop`ブランチを使用する例を紹介します。

1. 問題修正済みのリポジトリを取得する

   https://github.com/oreilly-japan/evogym から取得します。シミュレータのビルド時にサブモジュールのソースコードも使うため、サブモジュールも合わせて取得します。このリポジトリの`develop`ブランチには`macOS`用のビルドエラーに対応する修正が入っています。なお、本家にはプルリクエストを送付していますが、まだマージされていません。

   ```
   git clone --recursive https://github.com/oreilly-japan/evogym.git
   ```

2. 作業ディレクトリをリポジトリルートに移動する

   ソースコードを取得できたら、作業ディレクトリをリポジトリルートに移動します。

   ```
   cd evogym
   ```

3. venvを用いて仮想環境をを作成する

   `venv`を用いてPython 3.8の仮想環境を作成します。ここでは便宜上 `env-evogym` という名前で仮想環境を作成する事にします。

   ```
   python3.8 -m venv env-evogym .
   ```
4. 仮想環境をアクティベートする

   先程作成した仮想環境をアクティベートします。

   ```
   source env-evogym/bin/activate
   ```

5. 依存パッケージをインストールする

   依存パッケージをインストールします。

   ```
   pip install -r requirements.txt
   ```

6. `Evolution Gym`をインストールする

   `Evolution Gym`本体をインストールします。ここでは`pip`を用いることにします。インストール時にはシミュレータもビルドされるため、そこそこ時間がかかります。

   ```
   pip install .
   ```

7. 動作確認する

   インストールが完了したら、動作確認用のスクリプトを実行し、うまくいったかを確認します。

   ```
   python examples/gym_test.py
   ```

   以下のような画面が表示されたら、インストールは成功です。
   <img style="width: 100%;" src="/OpenEndedCodebook/img/example_f99vlj.png">

## 遭遇する可能性のあるエラー

先ほども述べたように、本家の`Evolution Gym`の主ブランチでは、環境によってはインストールエラーに遭遇することがあります。ここでは筆者が実際に遭遇したエラーと、その対応方法を紹介します。

### バージョンの不一致による失敗

環境によっては依存パッケージのインストールに失敗することがあります。これは`gym`と`stable-baselines3`のバージョンの食い違いや、`gym`の依存パッケージの宣言方法に問題があるため発生します。

対応としては、`gym`のバージョンを 0.20 以上にすることと、`stable-baselines3`をインストールしないことです。`stable-baselines3`は明示的に指定しなくても、他のパッケージの依存関係によりインストールされてしまいます。本家のリポジトリには、この問題に対応するプルリクエストがあるので、これを利用することで解決します。

https://github.com/EvolutionGym/evogym/pull/30

*依存パッケージのインストールに失敗する例*
```
$ pip install -r requirements.txt
  shell: /usr/bin/bash -e {0}
  env:
    pythonLocation: /opt/hostedtoolcache/Python/3.8.17/x64
    PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.8.17/x64/lib/pkgconfig
    LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.8.17/x64/lib
Collecting GPyOpt@ git+https://github.com/yunshengtian/GPyOpt@5fc1188ffdefea9a3bc7964a9414d4922603e904 (from -r requirements.txt (line 3))
  Cloning https://github.com/yunshengtian/GPyOpt (to revision 5fc1188ffdefea9a3bc7964a9414d4922603e904) to /tmp/pip-install-s2lwmj5k/gpyopt_80daa26ab4594821afe39b5dc00291d3
  Running command git clone --filter=blob:none --quiet https://github.com/yunshengtian/GPyOpt /tmp/pip-install-s2lwmj5k/gpyopt_80daa26ab4594821afe39b5dc00291d3
  Running command git rev-parse -q --verify 'sha^5fc1188ffdefea9a3bc7964a9414d4922603e904'
  Running command git fetch -q https://github.com/yunshengtian/GPyOpt 5fc1188ffdefea9a3bc7964a9414d4922603e904
  Resolved https://github.com/yunshengtian/GPyOpt to commit 5fc1188ffdefea9a3bc7964a9414d4922603e904
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Collecting neat-python@ git+https://github.com/yunshengtian/neat-python@2762ab630838520ca6c03a866e8a158f592b0370 (from -r requirements.txt (line 8))
  Cloning https://github.com/yunshengtian/neat-python (to revision 2762ab630838520ca6c03a866e8a158f592b0370) to /tmp/pip-install-s2lwmj5k/neat-python_9982b4be910e4e7daa10c7e40c302cea
  Running command git clone --filter=blob:none --quiet https://github.com/yunshengtian/neat-python /tmp/pip-install-s2lwmj5k/neat-python_9982b4be910e4e7daa10c7e40c302cea
  Running command git rev-parse -q --verify 'sha^2762ab630838520ca6c03a866e8a158f592b0370'
  Running command git fetch -q https://github.com/yunshengtian/neat-python 2762ab630838520ca6c03a866e8a158f592b0370
  Resolved https://github.com/yunshengtian/neat-python to commit 2762ab630838520ca6c03a866e8a158f592b0370
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Collecting setuptools==50.0.0
  Downloading setuptools-50.0.0-py3-none-any.whl (783 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 783.5/783.5 kB 5.2 MB/s eta 0:00:00
Requirement already satisfied: pip in /opt/hostedtoolcache/Python/3.8.17/x64/lib/python3.8/site-packages (23.0.1)
Collecting pip
  Obtaining dependency information for pip from https://files.pythonhosted.org/packages/50/c2/e06851e8cc28dcad7c155f4753da8833ac06a5c704c109313b8d5a62968a/pip-23.2.1-py3-none-any.whl.metadata
  Downloading pip-23.2.1-py3-none-any.whl.metadata (4.2 kB)
Collecting install
  Downloading install-1.3.5-py3-none-any.whl (3.2 kB)
Collecting pip
  Downloading pip-21.0-py3-none-any.whl (1.5 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.5/1.5 MB 15.7 MB/s eta 0:00:00
Collecting glfw==2.5.0 (from -r requirements.txt (line 1))
  Downloading glfw-2.5.0-py2.py27.py3.py30.py31.py32.py33.py34.py35.py36.py37.py38-none-manylinux2014_x86_64.whl (205 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 205.2/205.2 kB 11.9 MB/s eta 0:00:00
Collecting GPy==1.10.0 (from -r requirements.txt (line 2))
  Downloading GPy-1.10.0.tar.gz (959 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 959.4/959.4 kB 12.7 MB/s eta 0:00:00
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Installing backend dependencies: started
  Installing backend dependencies: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Collecting gym==0.22.0 (from -r requirements.txt (line 4))
  Downloading gym-0.22.0.tar.gz (631 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 631.1/631.1 kB 29.0 MB/s eta 0:00:00
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Collecting h5py==3.6.0 (from -r requirements.txt (line 5))
  Downloading h5py-3.6.0-cp38-cp38-manylinux_2_12_x86_64.manylinux2010_x86_64.whl (4.5 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.5/4.5 MB 40.0 MB/s eta 0:00:00
Collecting imageio==2.14.1 (from -r requirements.txt (line 6))
  Downloading imageio-2.14.1-py3-none-any.whl (3.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.3/3.3 MB 54.9 MB/s eta 0:00:00
Collecting matplotlib==3.5.1 (from -r requirements.txt (line 7))
  Downloading matplotlib-3.5.1-cp38-cp38-manylinux_2_5_x86_64.manylinux1_x86_64.whl (11.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 11.3/11.3 MB 59.9 MB/s eta 0:00:00
Collecting numpy==1.21.5 (from -r requirements.txt (line 9))
  Downloading numpy-1.21.5-cp38-cp38-manylinux_2_12_x86_64.manylinux2010_x86_64.whl (15.7 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 15.7/15.7 MB 48.2 MB/s eta 0:00:00
Collecting opencv-python==4.5.5.62 (from -r requirements.txt (line 10))
  Downloading opencv_python-4.5.5.62-cp36-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (60.4 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 60.4/60.4 MB 40.6 MB/s eta 0:00:00
Collecting Pillow==9.0.0 (from -r requirements.txt (line 11))
  Downloading Pillow-9.0.0-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.3/4.3 MB 95.3 MB/s eta 0:00:00
Collecting pybind11==2.9.0 (from -r requirements.txt (line 12))
  Downloading pybind11-2.9.0-py2.py3-none-any.whl (210 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 210.4/210.4 kB 46.2 MB/s eta 0:00:00
Collecting pygifsicle==1.0.5 (from -r requirements.txt (line 13))
  Downloading pygifsicle-1.0.5.tar.gz (5.2 kB)
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Collecting PyOpenGL==3.1.5 (from -r requirements.txt (line 14))
  Downloading PyOpenGL-3.1.5-py3-none-any.whl (2.4 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.4/2.4 MB 92.0 MB/s eta 0:00:00
Collecting PyOpenGL-accelerate==3.1.5 (from -r requirements.txt (line 15))
  Downloading PyOpenGL-accelerate-3.1.5.tar.gz (538 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 538.4/538.4 kB 39.9 MB/s eta 0:00:00
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Collecting stable-baselines3==1.4.0 (from -r requirements.txt (line 16))
  Downloading stable_baselines3-1.4.0-py3-none-any.whl (176 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 176.9/176.9 kB 36.3 MB/s eta 0:00:00
Collecting torch==1.10.2 (from -r requirements.txt (line 17))
  Downloading torch-1.10.2-cp38-cp38-manylinux1_x86_64.whl (881.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 881.9/881.9 MB 1.4 MB/s eta 0:00:00
Collecting ttkbootstrap==1.5.1 (from -r requirements.txt (line 18))
  Downloading ttkbootstrap-1.5.1-py3-none-any.whl (112 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 112.8/112.8 kB 12.7 MB/s eta 0:00:00
Collecting typing==3.7.4.3 (from -r requirements.txt (line 19))
  Downloading typing-3.7.4.3.tar.gz (78 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 78.6/78.6 kB 19.3 MB/s eta 0:00:00
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Collecting six (from GPy==1.10.0->-r requirements.txt (line 2))
  Downloading six-1.16.0-py2.py3-none-any.whl (11 kB)
Collecting paramz>=0.9.0 (from GPy==1.10.0->-r requirements.txt (line 2))
  Downloading paramz-0.9.5.tar.gz (71 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 71.3/71.3 kB 10.0 MB/s eta 0:00:00
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Collecting cython>=0.29 (from GPy==1.10.0->-r requirements.txt (line 2))
  Obtaining dependency information for cython>=0.29 from https://files.pythonhosted.org/packages/9f/17/26f46b499386a15065e930a160b8b169e49d264aa1d5c2751a7b4a676792/Cython-3.0.2-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata
  Downloading Cython-3.0.2-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (3.1 kB)
Collecting scipy>=1.3.0 (from GPy==1.10.0->-r requirements.txt (line 2))
  Downloading scipy-1.10.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (34.5 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 34.5/34.5 MB 37.8 MB/s eta 0:00:00
Collecting cloudpickle>=1.2.0 (from gym==0.22.0->-r requirements.txt (line 4))
  Downloading cloudpickle-2.2.1-py3-none-any.whl (25 kB)
Collecting gym-notices>=0.0.4 (from gym==0.22.0->-r requirements.txt (line 4))
  Downloading gym_notices-0.0.8-py3-none-any.whl (3.0 kB)
Collecting importlib-metadata>=4.10.0 (from gym==0.22.0->-r requirements.txt (line 4))
  Obtaining dependency information for importlib-metadata>=4.10.0 from https://files.pythonhosted.org/packages/cc/37/db7ba97e676af155f5fcb1a35466f446eadc9104e25b83366e8088c9c926/importlib_metadata-6.8.0-py3-none-any.whl.metadata
  Downloading importlib_metadata-6.8.0-py3-none-any.whl.metadata (5.1 kB)
Collecting cycler>=0.10 (from matplotlib==3.5.1->-r requirements.txt (line 7))
  Downloading cycler-0.11.0-py3-none-any.whl (6.4 kB)
Collecting fonttools>=4.22.0 (from matplotlib==3.5.1->-r requirements.txt (line 7))
  Obtaining dependency information for fonttools>=4.22.0 from https://files.pythonhosted.org/packages/91/f1/2379b341206a6e7e12f9d7c406ea03f0e0386eafa7913a47d8cc931cacf4/fonttools-4.42.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata
  Downloading fonttools-4.42.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (150 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 151.0/151.0 kB 25.8 MB/s eta 0:00:00
Collecting kiwisolver>=1.0.1 (from matplotlib==3.5.1->-r requirements.txt (line 7))
  Obtaining dependency information for kiwisolver>=1.0.1 from https://files.pythonhosted.org/packages/d2/55/7021ffcc8cb26a520bb051aa0a3d08daf200cde945e5863d5768161e2d3d/kiwisolver-1.4.5-cp38-cp38-manylinux_2_5_x86_64.manylinux1_x86_64.whl.metadata
  Downloading kiwisolver-1.4.5-cp38-cp38-manylinux_2_5_x86_64.manylinux1_x86_64.whl.metadata (6.4 kB)
Collecting packaging>=20.0 (from matplotlib==3.5.1->-r requirements.txt (line 7))
  Downloading packaging-23.1-py3-none-any.whl (48 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 48.9/48.9 kB 8.1 MB/s eta 0:00:00
Collecting pyparsing>=2.2.1 (from matplotlib==3.5.1->-r requirements.txt (line 7))
  Obtaining dependency information for pyparsing>=2.2.1 from https://files.pythonhosted.org/packages/39/92/8486ede85fcc088f1b3dba4ce92dd29d126fd96b0008ea213167940a2475/pyparsing-3.1.1-py3-none-any.whl.metadata
  Downloading pyparsing-3.1.1-py3-none-any.whl.metadata (5.1 kB)
Collecting python-dateutil>=2.7 (from matplotlib==3.5.1->-r requirements.txt (line 7))
  Downloading python_dateutil-2.8.2-py2.py3-none-any.whl (247 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 247.7/247.7 kB 27.5 MB/s eta 0:00:00
INFO: pip is looking at multiple versions of stable-baselines3 to determine which version is compatible with other requirements. This could take a while.
ERROR: Cannot install -r requirements.txt (line 16) and gym==0.22.0 because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested gym==0.22.0
    stable-baselines3 1.4.0 depends on gym<0.20 and >=0.17

To fix this you could try to:
1. loosen the range of package versions you've specified
2. remove package versions to allow pip attempt to solve the dependency conflict

ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/latest/topics/dependency-resolution/#dealing-with-dependency-conflicts

Notice:  A new release of pip is available: 23.0.1 -> 23.2.1
Notice:  To update, run: pip install --upgrade pip
```

### `GLEW`を見つけられないことによる失敗

Evolution Gymのリポジトリには`GLEW`のソースコードがサブモジュールとして`evogym/simulator/externals/glew`に登録されています。サブモジュールがそもそも取得できていない場合は、`git`コマンドを使ってサブモジュールを取得する必要があります。ただしサブモジュールが取得できていたとしても、インストールに失敗することがあります。その際は以下のようなエラーメッセージが出力されます。

*エラーメッセージ:*
```
Processing /private/tmp/b/evogym
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Building wheels for collected packages: evogym
  Building wheel for evogym (pyproject.toml) ... error
  error: subprocess-exited-with-error

  × Building wheel for evogym (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [135 lines of output]
      running bdist_wheel
      running build
      running build_py
      creating build
      creating build/lib.macosx-12-x86_64-cpython-38
      creating build/lib.macosx-12-x86_64-cpython-38/evogym
      copying evogym/world.py -> build/lib.macosx-12-x86_64-cpython-38/evogym
      copying evogym/sim.py -> build/lib.macosx-12-x86_64-cpython-38/evogym
      copying evogym/viewer.py -> build/lib.macosx-12-x86_64-cpython-38/evogym
      copying evogym/__init__.py -> build/lib.macosx-12-x86_64-cpython-38/evogym
      copying evogym/utils.py -> build/lib.macosx-12-x86_64-cpython-38/evogym
      creating build/lib.macosx-12-x86_64-cpython-38/evogym/envs
      copying evogym/envs/climb.py -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs
      copying evogym/envs/jump.py -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs
      copying evogym/envs/__init__.py -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs
      copying evogym/envs/traverse.py -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs
      copying evogym/envs/manipulate.py -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs
      copying evogym/envs/walk.py -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs
      copying evogym/envs/flip.py -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs
      copying evogym/envs/multi_goal.py -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs
      copying evogym/envs/change_shape.py -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs
      copying evogym/envs/balance.py -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs
      copying evogym/envs/base.py -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs
      creating build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/DownStepper-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/rigid_3x3.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Lifter-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Traverser-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Jumper-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Balancer-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/BidirectionalWalker-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files      copying evogym/envs/sim_files/GapJumper-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Thrower-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Balancer-v1.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Climber-v2.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/UpStepper-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Walker-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/CaveCrawler-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Climber-v1.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/package.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Climber-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/rigid_2x2.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/BridgeWalker-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Pusher-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Flipper-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/BeamSlider-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Carrier-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Hurdler-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/ObstacleTraverser-v1.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/ObstacleTraverser-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/ShapeChange.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/rigid_1x1.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/peg.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Carrier-v1.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/BeamToppler-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/PlatformJumper-v0.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      copying evogym/envs/sim_files/Pusher-v1.json -> build/lib.macosx-12-x86_64-cpython-38/evogym/envs/sim_files
      running build_ext
      CMake Deprecation Warning at CMakeLists.txt:1 (cmake_minimum_required):
        Compatibility with CMake < 3.5 will be removed from a future version of
        CMake.

        Update the VERSION argument <min> value or use a ...<max> suffix to tell
        CMake that the project does not need compatibility with older versions.


      -- The C compiler identification is AppleClang 15.0.0.15000040
      -- The CXX compiler identification is AppleClang 15.0.0.15000040
      -- Detecting C compiler ABI info
      -- Detecting C compiler ABI info - done
      -- Check for working C compiler: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/cc - skipped
      -- Detecting C compile features
      -- Detecting C compile features - done
      -- Detecting CXX compiler ABI info
      -- Detecting CXX compiler ABI info - done
      -- Check for working CXX compiler: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++ - skipped
      -- Detecting CXX compile features
      -- Detecting CXX compile features - done
      -- Found OpenGL: /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX14.0.sdk/System/Library/Frameworks/OpenGL.framework
      CMake Error at /usr/local/Cellar/cmake/3.27.1/share/cmake/Modules/FindPackageHandleStandardArgs.cmake:230 (message):
        Could NOT find GLEW (missing: GLEW_INCLUDE_DIRS GLEW_LIBRARIES)
      Call Stack (most recent call first):
        /usr/local/Cellar/cmake/3.27.1/share/cmake/Modules/FindPackageHandleStandardArgs.cmake:600 (_FPHSA_FAILURE_MESSAGE)
        /usr/local/Cellar/cmake/3.27.1/share/cmake/Modules/FindGLEW.cmake:238 (find_package_handle_standard_args)
        CMakeLists.txt:22 (find_package)


      -- Configuring incomplete, errors occurred!
      Traceback (most recent call last):
        File "/private/tmp/b/evogym/env-evogyma/lib/python3.8/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 353, in <module>
          main()
        File "/private/tmp/b/evogym/env-evogyma/lib/python3.8/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 335, in main
          json_out['return_val'] = hook(**hook_input['kwargs'])
        File "/private/tmp/b/evogym/env-evogyma/lib/python3.8/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 251, in build_wheel
          return _build_backend().build_wheel(wheel_directory, config_settings,
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/build_meta.py", line 434, in build_wheel
          return self._build_with_temp_dir(
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/build_meta.py", line 419, in _build_with_temp_dir
          self.run_setup()
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/build_meta.py", line 341, in run_setup
          exec(code, locals())
        File "<string>", line 61, in <module>
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/__init__.py", line 103, in setup
          return distutils.core.setup(**attrs)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/_distutils/core.py", line 185, in setup
          return run_commands(dist)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/_distutils/core.py", line 201, in run_commands
          dist.run_commands()
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/_distutils/dist.py", line 969, in run_commands
          self.run_command(cmd)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/dist.py", line 989, in run_command
          super().run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/_distutils/dist.py", line 988, in run_command
          cmd_obj.run()
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/wheel/bdist_wheel.py", line 364, in run
          self.run_command("build")
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/_distutils/cmd.py", line 318, in run_command
          self.distribution.run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/dist.py", line 989, in run_command
          super().run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/_distutils/dist.py", line 988, in run_command
          cmd_obj.run()
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/_distutils/command/build.py", line 131, in run
          self.run_command(cmd_name)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/_distutils/cmd.py", line 318, in run_command
          self.distribution.run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/dist.py", line 989, in run_command
          super().run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-qps3gd8u/overlay/lib/python3.8/site-packages/setuptools/_distutils/dist.py", line 988, in run_command
          cmd_obj.run()
        File "<string>", line 32, in run
        File "<string>", line 57, in build_extension
        File "/usr/local/Cellar/python@3.8/3.8.17_1/Frameworks/Python.framework/Versions/3.8/lib/python3.8/subprocess.py", line 364, in check_call
          raise CalledProcessError(retcode, cmd)
      subprocess.CalledProcessError: Command '['cmake', '/private/tmp/b/evogym/evogym/simulator', '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=/private/tmp/b/evogym/build/lib.macosx-12-x86_64-cpython-38/evogym', '-DPYTHON_EXECUTABLE=/private/tmp/b/evogym/env-evogyma/bin/python3.8', '-DCMAKE_BUILD_TYPE=Release']' returned non-zero exit status 1.
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for evogym
Failed to build evogym
ERROR: Could not build wheels for evogym, which is required to install pyproject.toml-based projects
```

次のエラーから、`GLEW`を見つけられていないことがわかります。

*`GLEW`を見つけられていない場合のエラーの例:*
```
      CMake Error at /usr/local/Cellar/cmake/3.27.1/share/cmake/Modules/FindPackageHandleStandardArgs.cmake:230 (message):
        Could NOT find GLEW (missing: GLEW_INCLUDE_DIRS GLEW_LIBRARIES)
      Call Stack (most recent call first):
        /usr/local/Cellar/cmake/3.27.1/share/cmake/Modules/FindPackageHandleStandardArgs.cmake:600 (_FPHSA_FAILURE_MESSAGE)
        /usr/local/Cellar/cmake/3.27.1/share/cmake/Modules/FindGLEW.cmake:238 (find_package_handle_standard_args)
        CMakeLists.txt:22 (find_package)
```

この`GLEW`は`cmake`が自動的に見つけてくれるものですが、`cmake`のバージョンによってはその機構(`FindGLEW.cmake`)が機能しません。その場合、`FindGLEW.cmake`を独自に用意する事で問題を回避できます。

`evogym/simulator/FindGLEW.cmake`ファイルを作成し、以下のように記述します。

*`evogym/simulator/FindGLEW.cmake`:*
```
# FindGLEW.cmake
# Search for GLEW library and include directories

find_path(GLEW_INCLUDE_DIR GL/glew.h)
find_library(GLEW_LIBRARY NAMES GLEW GLEW32)

if (GLEW_INCLUDE_DIR AND GLEW_LIBRARY)
    set(GLEW_FOUND TRUE)
else()
    set(GLEW_FOUND FALSE)
endif()

if (GLEW_FOUND)
    if (NOT GLEW_FIND_QUIETLY)
        message(STATUS "Found GLEW: ${GLEW_LIBRARY}")
    endif ()
else()
    if (GLEW_FIND_REQUIRED)
        message(FATAL_ERROR "Could NOT find GLEW")
    endif ()
endif()

mark_as_advanced(GLEW_INCLUDE_DIR GLEW_LIBRARY)
```

また、この独自の`FindGLEW.cmake`を`cmake`に使用させるため、`evogym/simulator/CMakeLists.txt`内に以下の 3 行を追加します。

*`evogym/simulator/CMakeLists.txt`の差分*
```
 if(UNIX)
   find_package(OpenGL REQUIRED)
+   set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR})  # use custom FindGLEW.cmak
+   set(GLEW_INCLUDE_DIR ${PROJECT_SOURCE_DIR}/externals/glew/include)
+   set(GLEW_LIBRARY ${PROJECT_SOURCE_DIR}/externals/glew/lib/libGLEW.*)
   find_package(GLEW REQUIRED)
 endif()
```

この修正でサブモジュールにある`GLEW`を見つけられるようになります。この対応は、本家のリポジトリのプルリクエスト https://github.com/EvolutionGym/evogym/pull/31 と同じものです。

### 型エラーによる失敗

`Evolution Gym`ではインストール時にシミュレータをビルドします。そのビルド時に問題があるとインストールに失敗します。型の宣言に間違いがあると、以下のようなエラーが発生します。

*型エラーによるビルドの失敗:*
```
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Environment.cpp:271:10: error: calling a private constructor of class 'Eigen::Ref<Eigen::Matrix<double, -1, -1>>'
                      return empty;
                             ^
      /tmp/b/evogym/evogym/simulator/externals/eigen/Eigen/src/Core/Ref.h:299:30: note: declared private here
          EIGEN_DEVICE_FUNC inline Ref(const PlainObjectBase<Derived>& expr,
                                   ^
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Environment.cpp:282:10: error: calling a private constructor of class 'Eigen::Ref<Eigen::Matrix<double, -1, -1>>'
                      return empty;
                             ^
      /tmp/b/evogym/evogym/simulator/externals/eigen/Eigen/src/Core/Ref.h:299:30: note: declared private here
          EIGEN_DEVICE_FUNC inline Ref(const PlainObjectBase<Derived>& expr,
                                   ^
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Environment.cpp:294:10: error: calling a private constructor of class 'Eigen::Ref<Eigen::Matrix<double, -1, -1>>'
                      return empty;
                             ^
      /tmp/b/evogym/evogym/simulator/externals/eigen/Eigen/src/Core/Ref.h:299:30: note: declared private here
          EIGEN_DEVICE_FUNC inline Ref(const PlainObjectBase<Derived>& expr,
                                   ^
      [ 92%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/SimObject.cpp.o
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Environment.cpp:309:10: error: calling a private constructor of class 'Eigen::Ref<Eigen::Matrix<double, -1, -1>>'
                      return empty;
                             ^
      /tmp/b/evogym/evogym/simulator/externals/eigen/Eigen/src/Core/Ref.h:299:30: note: declared private here
          EIGEN_DEVICE_FUNC inline Ref(const PlainObjectBase<Derived>& expr,
                                   ^
      1 warning generated.
      [ 95%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/Snapshot.cpp.o
      4 errors generated.
      make[2]: *** [SimulatorCPP/CMakeFiles/simulator_cpp.dir/Environment.cpp.o] Error 1
      make[2]: *** Waiting for unfinished jobs....
      25 warnings generated.
      In file included from /tmp/b/evogym/evogym/simulator/SimulatorCPP/Sim.cpp:1:
      In file included from /tmp/b/evogym/evogym/simulator/SimulatorCPP/Sim.h:9:
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.h:9:23: warning: extra tokens at end of #include directive [-Wextra-tokens]
      #include "SimObject.h";
                            ^
                            //
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Sim.cpp:19:28: warning: assigning field to itself [-Wself-assign-field]
              Sim::is_rendering_enabled = is_rendering_enabled;
                                        ^
      2 warnings generated.
      1 warning generated.
      make[1]: *** [SimulatorCPP/CMakeFiles/simulator_cpp.dir/all] Error 2
      make: *** [all] Error 2
```

このエラーが出る場合は型宣言を変更するか、読み込んでいるライブラリとの辻褄を合わせる必要があります。今回は型宣言を変更する方法をとります。エラーメッセージをよく見ると、どんな型に変更すればよいか出力されているので、それに置換します。問題となるコードは全て`evogym/simulator/SimulatorCPP`配下にあるため、この中にある該当のコードを`grep`し、コンパイラが出力した型に置き換えればよいのです。

なお、本家のリポジトリには、これに対応したプルリクエストがあります。 https://github.com/EvolutionGym/evogym/pull/32

*型エラーでインストール失敗時の出力:*
```
Processing /private/tmp/b/evogym
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Building wheels for collected packages: evogym
  Building wheel for evogym (pyproject.toml) ... error
  error: subprocess-exited-with-error

  × Building wheel for evogym (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [330 lines of output]
      running bdist_wheel
      running build
      running build_py
      running build_ext
      CMake Deprecation Warning at CMakeLists.txt:1 (cmake_minimum_required):
        Compatibility with CMake < 3.5 will be removed from a future version of
        CMake.

        Update the VERSION argument <min> value or use a ...<max> suffix to tell
        CMake that the project does not need compatibility with older versions.


      -- Found GLEW: /tmp/b/evogym/evogym/simulator/externals/glew/lib/libGLEW.*
      CMake Deprecation Warning at externals/CMakeLists.txt:2 (cmake_minimum_required):
        Compatibility with CMake < 3.5 will be removed from a future version of
        CMake.

        Update the VERSION argument <min> value or use a ...<max> suffix to tell
        CMake that the project does not need compatibility with older versions.


      CMake Deprecation Warning at externals/pybind11/CMakeLists.txt:8 (cmake_minimum_required):
        Compatibility with CMake < 3.5 will be removed from a future version of
        CMake.

        Update the VERSION argument <min> value or use a ...<max> suffix to tell
        CMake that the project does not need compatibility with older versions.


      -- pybind11 v2.9.0
      CMake Warning (dev) at externals/pybind11/tools/FindPythonLibsNew.cmake:98 (find_package):
        Policy CMP0148 is not set: The FindPythonInterp and FindPythonLibs modules
        are removed.  Run "cmake --help-policy CMP0148" for policy details.  Use
        the cmake_policy command to set the policy and suppress this warning.

      Call Stack (most recent call first):
        externals/pybind11/tools/pybind11Tools.cmake:50 (find_package)
        externals/pybind11/tools/pybind11Common.cmake:206 (include)
        externals/pybind11/CMakeLists.txt:200 (include)
      This warning is for project developers.  Use -Wno-dev to suppress it.

      -- Found PythonInterp: /private/tmp/b/evogym/env-evogyma/bin/python3.8 (found version "3.8.17")
      -- Found PythonLibs: /usr/local/opt/python@3.8/Frameworks/Python.framework/Versions/3.8/lib/libpython3.8.dylib
      -- Performing Test HAS_FLTO
      -- Performing Test HAS_FLTO - Success
      -- Performing Test HAS_FLTO_THIN
      -- Performing Test HAS_FLTO_THIN - Success
      -- Performing Test CMAKE_HAVE_LIBC_PTHREAD
      -- Performing Test CMAKE_HAVE_LIBC_PTHREAD - Success
      -- Found Threads: TRUE
      -- Found Doxygen: /usr/local/bin/doxygen (found version "1.9.7") found components: doxygen
      -- Including Cocoa support
      -- Configuring done (2.0s)
      -- Generating done (0.0s)
      -- Build files have been written to: /tmp/b/evogym/build/temp.macosx-12-x86_64-cpython-38
      [  2%] Generating HTML documentation
      [  7%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/context.c.o
      [  7%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/init.c.o
      [ 10%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/input.c.o
      [ 12%] Building C object externals/CMakeFiles/glew.dir/glew/src/glew.c.o
      [ 17%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/platform.c.o
      [ 17%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/monitor.c.o
      [ 20%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/vulkan.c.o
      warning: Tag 'HTML_TIMESTAMP' at line 1219 of file 'Doxyfile' has become obsolete.
               To avoid this warning please remove this line from your configuration file or upgrade it using "doxygen -u"
      warning: Tag 'FORMULA_TRANSPARENT' at line 1522 of file 'Doxyfile' has become obsolete.
               To avoid this warning please remove this line from your configuration file or upgrade it using "doxygen -u"
      warning: Tag 'LATEX_TIMESTAMP' at line 1836 of file 'Doxyfile' has become obsolete.
               To avoid this warning please remove this line from your configuration file or upgrade it using "doxygen -u"
      warning: Tag 'CLASS_DIAGRAMS' at line 2193 of file 'Doxyfile' has become obsolete.
               To avoid this warning please remove this line from your configuration file or upgrade it using "doxygen -u"
      warning: Tag 'DOT_FONTNAME' at line 2235 of file 'Doxyfile' has become obsolete.
               To avoid this warning please remove this line from your configuration file or upgrade it using "doxygen -u"
      warning: Tag 'DOT_FONTSIZE' at line 2242 of file 'Doxyfile' has become obsolete.
               To avoid this warning please remove this line from your configuration file or upgrade it using "doxygen -u"
      warning: Tag 'DOT_TRANSPARENT' at line 2466 of file 'Doxyfile' has become obsolete.
               To avoid this warning please remove this line from your configuration file or upgrade it using "doxygen -u"
      [ 20%] Built target docs
      [ 22%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/window.c.o
      [ 25%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/egl_context.c.o
      [ 27%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/osmesa_context.c.o
      [ 30%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/null_init.c.o
      [ 32%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/null_monitor.c.o
      [ 35%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/null_window.c.o
      [ 37%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/null_joystick.c.o
      [ 40%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/cocoa_time.c.o
      [ 42%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/posix_module.c.o
      [ 45%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/posix_thread.c.o
      [ 47%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/cocoa_init.m.o
      [ 50%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/cocoa_joystick.m.o
      [ 52%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/cocoa_monitor.m.o
      [ 55%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/cocoa_window.m.o
      [ 57%] Building C object externals/glfw/src/CMakeFiles/glfw.dir/nsgl_context.m.o
      /tmp/b/evogym/evogym/simulator/externals/glfw/src/cocoa_window.m:366:62: warning: 'kUTTypeURL' is deprecated: first deprecated in macOS 12.0 - Use UTTypeURL or UTType.url (swift) instead. [-Wdeprecated-declarations]
              [self registerForDraggedTypes:@[(__bridge NSString*) kUTTypeURL]];
                                                                   ^
      /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX14.0.sdk/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Headers/UTCoreTypes.h:210:26: note: 'kUTTypeURL' has been explicitly marked deprecated here
      extern const CFStringRef kUTTypeURL                                  API_DEPRECATED("Use UTTypeURL or UTType.url (swift) instead.", ios(3.0, 15.0), macos(10.4, 12.0), tvos(9.0, 15.0), watchos(1.0, 8.0));
                               ^
      1 warning generated.
      [ 60%] Linking C static library libglfw3.a
      [ 60%] Built target glfw
      [ 62%] Linking C static library libglew.a
      [ 62%] Built target glew
      [ 65%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/ObjectCreator.cpp.o
      [ 67%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/Camera.cpp.o
      [ 70%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/PythonBindings.cpp.o
      [ 72%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/Environment.cpp.o
      [ 75%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/Boxel.cpp.o
      [ 77%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/BBTreeNode.cpp.o
      [ 80%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/Edge.cpp.o
      [ 82%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/Interface.cpp.o
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Boxel.cpp:6:26: warning: implicit conversion of NULL constant to 'int' [-Wnull-conversion]
              point_top_right_index = NULL;
                                    ~ ^~~~
                                      0
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Boxel.cpp:7:25: warning: implicit conversion of NULL constant to 'int' [-Wnull-conversion]
              point_top_left_index = NULL;
                                   ~ ^~~~
                                     0
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Boxel.cpp:8:26: warning: implicit conversion of NULL constant to 'int' [-Wnull-conversion]
              point_bot_right_index = NULL;
                                    ~ ^~~~
                                      0
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Boxel.cpp:9:25: warning: implicit conversion of NULL constant to 'int' [-Wnull-conversion]
              point_bot_left_index = NULL;
                                   ~ ^~~~
                                     0
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Boxel.cpp:11:19: warning: implicit conversion of NULL constant to 'int' [-Wnull-conversion]
              edge_top_index = NULL;
                             ~ ^~~~
                               0
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Boxel.cpp:12:19: warning: implicit conversion of NULL constant to 'int' [-Wnull-conversion]
              edge_bot_index = NULL;
                             ~ ^~~~
                               0
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Boxel.cpp:13:20: warning: implicit conversion of NULL constant to 'int' [-Wnull-conversion]
              edge_left_index = NULL;
                              ~ ^~~~
                                0
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Boxel.cpp:14:21: warning: implicit conversion of NULL constant to 'int' [-Wnull-conversion]
              edge_right_index = NULL;
                               ~ ^~~~
                                 0
      [ 85%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/PhysicsEngine.cpp.o
      In file included from /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:1:
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.h:9:23: warning: extra tokens at end of #include directive [-Wextra-tokens]
      #include "SimObject.h";
                            ^
                            //
      In file included from /tmp/b/evogym/evogym/simulator/SimulatorCPP/Interface.cpp:1:
      In file included from /tmp/b/evogym/evogym/simulator/SimulatorCPP/Interface.h:13:
      In file included from /tmp/b/evogym/evogym/simulator/SimulatorCPP/Sim.h:9:
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.h:9:23: warning: extra tokens at end of #include directive [-Wextra-tokens]
      #include "SimObject.h";
                            ^
                            //
      [ 87%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/Robot.cpp.o
      In file included from /tmp/b/evogym/evogym/simulator/SimulatorCPP/PythonBindings.cpp:3:
      In file included from /tmp/b/evogym/evogym/simulator/SimulatorCPP/Interface.h:13:
      In file included from /tmp/b/evogym/evogym/simulator/SimulatorCPP/Sim.h:9:
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.h:9:23: warning: extra tokens at end of #include directive [-Wextra-tokens]
      #include "SimObject.h";
                            ^
                            //
      [ 90%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/Sim.cpp.o
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:334:49: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (top != NULL && top->point_bot_left_index != NULL)
                                                 ~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:336:52: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (left != NULL && left->point_top_right_index != NULL)
                                                  ~~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:338:60: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (top_left != NULL && top_left->point_bot_right_index != NULL)
                                                      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:340:38: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (current->point_top_left_index == NULL)
                                  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:349:50: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (top != NULL && top->point_bot_right_index != NULL)
                                                 ~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:351:53: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (right != NULL && right->point_top_left_index != NULL)
                                                   ~~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:353:61: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (top_right != NULL && top_right->point_bot_left_index != NULL)
                                                       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:355:39: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (current->point_top_right_index == NULL)
                                  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:364:49: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (bot != NULL && bot->point_top_left_index != NULL)
                                                 ~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:366:52: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (left != NULL && left->point_bot_right_index != NULL)
                                                  ~~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:368:60: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (bot_left != NULL && bot_left->point_top_right_index != NULL)
                                                      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:370:38: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (current->point_bot_left_index == NULL)
                                  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:380:50: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (bot != NULL && bot->point_top_right_index != NULL)
                                                 ~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:382:53: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (right != NULL && right->point_bot_left_index != NULL)
                                                   ~~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:384:61: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (bot_right != NULL && bot_right->point_top_left_index != NULL)
                                                       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:386:39: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (current->point_bot_right_index == NULL)
                                  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:398:43: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (top != NULL && top->edge_bot_index != NULL)
                                                 ~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:400:32: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (current->edge_top_index == NULL) {
                                  ~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:405:43: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (bot != NULL && bot->edge_top_index != NULL)
                                                 ~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:407:32: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (current->edge_bot_index == NULL) {
                                  ~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:412:47: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (left != NULL && left->edge_right_index != NULL)
                                                  ~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:414:33: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (current->edge_left_index == NULL) {
                                  ~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:419:48: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (right != NULL && right->edge_left_index != NULL)
                                                   ~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.cpp:421:34: warning: comparison between NULL and non-pointer ('int' and NULL) [-Wnull-arithmetic]
                              if (current->edge_right_index == NULL) {
                                  ~~~~~~~~~~~~~~~~~~~~~~~~~ ^  ~~~~
      8 warnings generated.
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Environment.cpp:271:10: error: calling a private constructor of class 'Eigen::Ref<Eigen::Matrix<double, -1, -1>>'
                      return empty;
                             ^
      /tmp/b/evogym/evogym/simulator/externals/eigen/Eigen/src/Core/Ref.h:299:30: note: declared private here
          EIGEN_DEVICE_FUNC inline Ref(const PlainObjectBase<Derived>& expr,
                                   ^
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Environment.cpp:282:10: error: calling a private constructor of class 'Eigen::Ref<Eigen::Matrix<double, -1, -1>>'
                      return empty;
                             ^
      /tmp/b/evogym/evogym/simulator/externals/eigen/Eigen/src/Core/Ref.h:299:30: note: declared private here
          EIGEN_DEVICE_FUNC inline Ref(const PlainObjectBase<Derived>& expr,
                                   ^
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Environment.cpp:294:10: error: calling a private constructor of class 'Eigen::Ref<Eigen::Matrix<double, -1, -1>>'
                      return empty;
                             ^
      /tmp/b/evogym/evogym/simulator/externals/eigen/Eigen/src/Core/Ref.h:299:30: note: declared private here
          EIGEN_DEVICE_FUNC inline Ref(const PlainObjectBase<Derived>& expr,
                                   ^
      [ 92%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/SimObject.cpp.o
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Environment.cpp:309:10: error: calling a private constructor of class 'Eigen::Ref<Eigen::Matrix<double, -1, -1>>'
                      return empty;
                             ^
      /tmp/b/evogym/evogym/simulator/externals/eigen/Eigen/src/Core/Ref.h:299:30: note: declared private here
          EIGEN_DEVICE_FUNC inline Ref(const PlainObjectBase<Derived>& expr,
                                   ^
      1 warning generated.
      [ 95%] Building CXX object SimulatorCPP/CMakeFiles/simulator_cpp.dir/Snapshot.cpp.o
      4 errors generated.
      make[2]: *** [SimulatorCPP/CMakeFiles/simulator_cpp.dir/Environment.cpp.o] Error 1
      make[2]: *** Waiting for unfinished jobs....
      25 warnings generated.
      In file included from /tmp/b/evogym/evogym/simulator/SimulatorCPP/Sim.cpp:1:
      In file included from /tmp/b/evogym/evogym/simulator/SimulatorCPP/Sim.h:9:
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/ObjectCreator.h:9:23: warning: extra tokens at end of #include directive [-Wextra-tokens]
      #include "SimObject.h";
                            ^
                            //
      /tmp/b/evogym/evogym/simulator/SimulatorCPP/Sim.cpp:19:28: warning: assigning field to itself [-Wself-assign-field]
              Sim::is_rendering_enabled = is_rendering_enabled;
                                        ^
      2 warnings generated.
      1 warning generated.
      make[1]: *** [SimulatorCPP/CMakeFiles/simulator_cpp.dir/all] Error 2
      make: *** [all] Error 2
      Traceback (most recent call last):
        File "/private/tmp/b/evogym/env-evogyma/lib/python3.8/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 353, in <module>
          main()
        File "/private/tmp/b/evogym/env-evogyma/lib/python3.8/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 335, in main
          json_out['return_val'] = hook(**hook_input['kwargs'])
        File "/private/tmp/b/evogym/env-evogyma/lib/python3.8/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 251, in build_wheel
          return _build_backend().build_wheel(wheel_directory, config_settings,
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/build_meta.py", line 434, in build_wheel
          return self._build_with_temp_dir(
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/build_meta.py", line 419, in _build_with_temp_dir
          self.run_setup()
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/build_meta.py", line 341, in run_setup
          exec(code, locals())
        File "<string>", line 61, in <module>
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/__init__.py", line 103, in setup
          return distutils.core.setup(**attrs)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/_distutils/core.py", line 185, in setup
          return run_commands(dist)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/_distutils/core.py", line 201, in run_commands
          dist.run_commands()
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/_distutils/dist.py", line 969, in run_commands
          self.run_command(cmd)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/dist.py", line 989, in run_command
          super().run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/_distutils/dist.py", line 988, in run_command
          cmd_obj.run()
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/wheel/bdist_wheel.py", line 364, in run
          self.run_command("build")
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/_distutils/cmd.py", line 318, in run_command
          self.distribution.run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/dist.py", line 989, in run_command
          super().run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/_distutils/dist.py", line 988, in run_command
          cmd_obj.run()
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/_distutils/command/build.py", line 131, in run
          self.run_command(cmd_name)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/_distutils/cmd.py", line 318, in run_command
          self.distribution.run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/dist.py", line 989, in run_command
          super().run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-9ub8i7m6/overlay/lib/python3.8/site-packages/setuptools/_distutils/dist.py", line 988, in run_command
          cmd_obj.run()
        File "<string>", line 32, in run
        File "<string>", line 58, in build_extension
        File "/usr/local/Cellar/python@3.8/3.8.17_1/Frameworks/Python.framework/Versions/3.8/lib/python3.8/subprocess.py", line 364, in check_call
          raise CalledProcessError(retcode, cmd)
      subprocess.CalledProcessError: Command '['cmake', '--build', '.', '--config', 'Release', '--', '-j8']' returned non-zero exit status 2.
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for evogym
Failed to build evogym
ERROR: Could not build wheels for evogym, which is required to install pyproject.toml-based projects
```

### h5pyのインストールに失敗する

環境によっては`h5py`のインストールに失敗する事があります。本書では読者からのご指摘を頂き、この問題について調査を行いました。

`Evolution Gym`の`requirements.txt`には`h5py-3.6.0`が記述されています。`h5py-3.6.0`は、環境によって`whl`形式のパッケージが用事されていますが、用意されていない環境もあります。`whl`形式のパッケージにはビルド済みバイナリが梱包されています。もし、お使いの環境に対応する`whl`形式が用意されていない場合、ソースコードのtarballをダウンロードしビルドが行われます。しかしビルドの環境が整っていなけければ、ビルドに失敗するでしょう。以下に、ビルド失敗の出力の例を示します。

```
$ pip install 'h5py==3.6.0' --no-binary=h5py
Collecting h5py==3.6.0
  Using cached h5py-3.6.0.tar.gz (384 kB)
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Requirement already satisfied: numpy>=1.14.5 in /Users/foo/.venv/testing-h5py/lib/python3.8/site-packages (from h5py==3.6.0) (1.21.5)
Building wheels for collected packages: h5py
  Building wheel for h5py (pyproject.toml): started
  Building wheel for h5py (pyproject.toml): finished with status 'error'
  error: subprocess-exited-with-error

  × Building wheel for h5py (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [528 lines of output]
      running bdist_wheel
      running build
      running build_py
      creating build
      creating build/lib.macosx-13-x86_64-cpython-38
      creating build/lib.macosx-13-x86_64-cpython-38/h5py
      copying h5py/h5py_warnings.py -> build/lib.macosx-13-x86_64-cpython-38/h5py
      copying h5py/version.py -> build/lib.macosx-13-x86_64-cpython-38/h5py
      copying h5py/__init__.py -> build/lib.macosx-13-x86_64-cpython-38/h5py
      copying h5py/ipy_completer.py -> build/lib.macosx-13-x86_64-cpython-38/h5py
      creating build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      copying h5py/_hl/files.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      copying h5py/_hl/compat.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      copying h5py/_hl/__init__.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      copying h5py/_hl/selections.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      copying h5py/_hl/dataset.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      copying h5py/_hl/vds.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      copying h5py/_hl/selections2.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      copying h5py/_hl/group.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      copying h5py/_hl/datatype.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      copying h5py/_hl/attrs.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      copying h5py/_hl/dims.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      copying h5py/_hl/base.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      copying h5py/_hl/filters.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/_hl
      creating build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_dimension_scales.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_attribute_create.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_file_image.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/conftest.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_h5d_direct_chunk.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_h5f.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_dataset_getitem.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_group.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_errors.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_dataset_swmr.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_slicing.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_h5pl.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_attrs.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/__init__.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_attrs_data.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_h5t.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_big_endian_file.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_h5p.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_dims_dimensionproxy.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_h5o.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_datatype.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/common.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_dataset.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_file.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_selections.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_dtype.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_h5.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_file2.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_completions.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_filters.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_base.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      copying h5py/tests/test_objects.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests
      creating build/lib.macosx-13-x86_64-cpython-38/h5py/tests/data_files
      copying h5py/tests/data_files/__init__.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests/data_files
      creating build/lib.macosx-13-x86_64-cpython-38/h5py/tests/test_vds
      copying h5py/tests/test_vds/test_highlevel_vds.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests/test_vds
      copying h5py/tests/test_vds/test_virtual_source.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests/test_vds
      copying h5py/tests/test_vds/__init__.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests/test_vds
      copying h5py/tests/test_vds/test_lowlevel_vds.py -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests/test_vds
      copying h5py/tests/data_files/vlen_string_s390x.h5 -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests/data_files
      copying h5py/tests/data_files/vlen_string_dset_utc.h5 -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests/data_files
      copying h5py/tests/data_files/vlen_string_dset.h5 -> build/lib.macosx-13-x86_64-cpython-38/h5py/tests/data_files
      running build_ext
      warning: h5py/defs.pxd:15:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:62:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:64:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:66:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:68:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:70:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:72:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:74:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:76:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:78:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:102:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:104:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:106:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:107:4: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:109:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:110:4: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:112:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:114:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:116:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:180:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:197:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:199:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:201:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:203:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:213:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:215:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:229:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:231:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:233:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:235:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:237:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:239:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:241:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:269:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:271:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:273:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:275:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:277:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:279:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:285:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:287:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:289:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:291:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:293:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:295:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:297:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:299:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:333:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:335:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:337:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:339:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:341:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:343:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:345:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:347:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:349:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:383:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/defs.pxd:385:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/api_types_hdf5.pxd:48:2: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/api_types_hdf5.pxd:64:2: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/api_types_hdf5.pxd:143:2: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/api_types_hdf5.pxd:148:2: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/api_types_hdf5.pxd:156:2: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/api_types_hdf5.pxd:165:2: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/api_types_hdf5.pxd:198:2: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/api_types_hdf5.pxd:287:2: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/api_types_hdf5.pxd:334:2: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/api_types_ext.pxd:14:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/api_types_ext.pxd:25:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/api_types_ext.pxd:52:4: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/_conv.pyx:161:8: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/_conv.pyx:422:8: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310
      warning: h5py/h5r.pxd:17:0: The 'IF' statement is deprecated and will be removed in a future Cython version. Consider using runtime conditions or C macros instead. See https://github.com/cython/cython/issues/4310

      Error compiling Cython file:
      ------------------------------------------------------------
      ...
      # License:  Standard 3-clause BSD; see "license.txt" for full license terms
      #           and contributor agreement.

      from .defs cimport *

      from ._objects cimport class ObjectID
                             ^
      ------------------------------------------------------------

      h5py/h5t.pxd:13:23: Expected an identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...

      from logging import getLogger

      from .h5 import get_config
      from .h5r cimport Reference, RegionReference, hobj_ref_t, hdset_reg_ref_t
      from .h5t cimport H5PY_OBJ, typewrap, py_create, TypeID, H5PY_PYTHON_OPAQUE_TAG
      ^
      ------------------------------------------------------------

      h5py/_conv.pyx:21:0: 'h5py/h5t/H5PY_OBJ.pxd' not found

      Error compiling Cython file:
      ------------------------------------------------------------
      ...

      from logging import getLogger

      from .h5 import get_config
      from .h5r cimport Reference, RegionReference, hobj_ref_t, hdset_reg_ref_t
      from .h5t cimport H5PY_OBJ, typewrap, py_create, TypeID, H5PY_PYTHON_OPAQUE_TAG
      ^
      ------------------------------------------------------------

      h5py/_conv.pyx:21:0: 'h5py/h5t/typewrap.pxd' not found

      Error compiling Cython file:
      ------------------------------------------------------------
      ...

      from logging import getLogger

      from .h5 import get_config
      from .h5r cimport Reference, RegionReference, hobj_ref_t, hdset_reg_ref_t
      from .h5t cimport H5PY_OBJ, typewrap, py_create, TypeID, H5PY_PYTHON_OPAQUE_TAG
      ^
      ------------------------------------------------------------

      h5py/_conv.pyx:21:0: 'h5py/h5t/py_create.pxd' not found

      Error compiling Cython file:
      ------------------------------------------------------------
      ...

      from logging import getLogger

      from .h5 import get_config
      from .h5r cimport Reference, RegionReference, hobj_ref_t, hdset_reg_ref_t
      from .h5t cimport H5PY_OBJ, typewrap, py_create, TypeID, H5PY_PYTHON_OPAQUE_TAG
      ^
      ------------------------------------------------------------

      h5py/_conv.pyx:21:0: 'h5py/h5t/TypeID.pxd' not found

      Error compiling Cython file:
      ------------------------------------------------------------
      ...

      from logging import getLogger

      from .h5 import get_config
      from .h5r cimport Reference, RegionReference, hobj_ref_t, hdset_reg_ref_t
      from .h5t cimport H5PY_OBJ, typewrap, py_create, TypeID, H5PY_PYTHON_OPAQUE_TAG
      ^
      ------------------------------------------------------------

      h5py/_conv.pyx:21:0: 'h5py/h5t/H5PY_PYTHON_OPAQUE_TAG.pxd' not found

      Error compiling Cython file:
      ------------------------------------------------------------
      ...
          void* ptr

      cdef int conv_vlen2ndarray(void* ipt,
                                 void* opt,
                                 cnp.dtype elem_dtype,
                                 TypeID intype,
                                 ^
      ------------------------------------------------------------

      h5py/_conv.pyx:687:27: 'TypeID' is not a type identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...

      cdef int conv_vlen2ndarray(void* ipt,
                                 void* opt,
                                 cnp.dtype elem_dtype,
                                 TypeID intype,
                                 TypeID outtype) except -1:
                                 ^
      ------------------------------------------------------------

      h5py/_conv.pyx:688:27: 'TypeID' is not a type identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...
          return 0


      cdef int conv_ndarray2vlen(void* ipt,
                                 void* opt,
                                 TypeID intype,
                                 ^
      ------------------------------------------------------------

      h5py/_conv.pyx:820:27: 'TypeID' is not a type identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...


      cdef int conv_ndarray2vlen(void* ipt,
                                 void* opt,
                                 TypeID intype,
                                 TypeID outtype) except -1:
                                 ^
      ------------------------------------------------------------

      h5py/_conv.pyx:821:27: 'TypeID' is not a type identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...
          :return: error-code
          """
          cdef:
              int command = cdata[0].command
              size_t src_size, dst_size
              TypeID supertype
              ^
      ------------------------------------------------------------

      h5py/_conv.pyx:629:8: 'TypeID' is not a type identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...
          """
          cdef:
              int command = cdata[0].command
              size_t src_size, dst_size
              TypeID supertype
              TypeID outtype
              ^
      ------------------------------------------------------------

      h5py/_conv.pyx:630:8: 'TypeID' is not a type identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...
                               void *bkg_i,
                               hid_t dxpl) except -1 with gil:
          cdef:
              int command = cdata[0].command
              size_t src_size, dst_size
              TypeID supertype
              ^
      ------------------------------------------------------------

      h5py/_conv.pyx:752:8: 'TypeID' is not a type identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...
                               hid_t dxpl) except -1 with gil:
          cdef:
              int command = cdata[0].command
              size_t src_size, dst_size
              TypeID supertype
              TypeID outtype
              ^
      ------------------------------------------------------------

      h5py/_conv.pyx:753:8: 'TypeID' is not a type identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...
          cdef char* ctag = NULL
          try:
              if H5Tget_class(obj) == H5T_OPAQUE:
                  ctag = H5Tget_tag(obj)
                  if ctag != NULL:
                      if strcmp(ctag, H5PY_PYTHON_OPAQUE_TAG) == 0:
                                      ^
      ------------------------------------------------------------

      h5py/_conv.pyx:157:32: 'H5PY_PYTHON_OPAQUE_TAG' is not a constant, variable or function identifier
      warning: h5py/_conv.pyx:157:32: Obtaining 'const char *' from externally modifiable global Python value

      Error compiling Cython file:
      ------------------------------------------------------------
      ...
          elif command == H5T_CONV_FREE:
              pass

          elif command == H5T_CONV_CONV:
              # need to pass element dtype to converter
              supertype = typewrap(H5Tget_super(src_id))
                          ^
      ------------------------------------------------------------

      h5py/_conv.pyx:645:20: 'typewrap' is not a constant, variable or function identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...

          elif command == H5T_CONV_CONV:
              # need to pass element dtype to converter
              supertype = typewrap(H5Tget_super(src_id))
              dt = supertype.dtype
              outtype = py_create(dt)
                        ^
      ------------------------------------------------------------

      h5py/_conv.pyx:647:18: 'py_create' is not a constant, variable or function identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...
              PyObject *pdata_elem
              char* buf = <char*>buf_i

          if command == H5T_CONV_INIT:
              cdata[0].need_bkg = H5T_BKG_NO
              if not H5Tequal(src_id, H5PY_OBJ) or H5Tget_class(dst_id) != H5T_VLEN:
                                      ^
      ------------------------------------------------------------

      h5py/_conv.pyx:761:32: 'H5PY_OBJ' is not a constant, variable or function identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...

          if command == H5T_CONV_INIT:
              cdata[0].need_bkg = H5T_BKG_NO
              if not H5Tequal(src_id, H5PY_OBJ) or H5Tget_class(dst_id) != H5T_VLEN:
                  return -2
              supertype = typewrap(H5Tget_super(dst_id))
                          ^
      ------------------------------------------------------------

      h5py/_conv.pyx:763:20: 'typewrap' is not a constant, variable or function identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...
                  return -2
              supertype = typewrap(H5Tget_super(dst_id))
              for i in range(nl):
                  # smells a lot
                  memcpy(&pdata_elem, pdata+i, sizeof(pdata_elem))
                  if supertype != py_create((<cnp.ndarray> pdata_elem).dtype, 1):
                                  ^
      ------------------------------------------------------------

      h5py/_conv.pyx:767:28: 'py_create' is not a constant, variable or function identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...
              if nl == 0:
                  return 0

              # need to pass element dtype to converter
              pdata_elem = pdata[0]
              supertype = py_create((<cnp.ndarray> pdata_elem).dtype)
                          ^
      ------------------------------------------------------------

      h5py/_conv.pyx:784:20: 'py_create' is not a constant, variable or function identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...
                  return 0

              # need to pass element dtype to converter
              pdata_elem = pdata[0]
              supertype = py_create((<cnp.ndarray> pdata_elem).dtype)
              outtype = typewrap(H5Tget_super(dst_id))
                        ^
      ------------------------------------------------------------

      h5py/_conv.pyx:785:18: 'typewrap' is not a constant, variable or function identifier

      Error compiling Cython file:
      ------------------------------------------------------------
      ...

          enum = H5Tenum_create(H5T_STD_I32LE)

          vlentype = H5Tvlen_create(H5T_STD_I32LE)

          pyobj = H5PY_OBJ
                  ^
      ------------------------------------------------------------

      h5py/_conv.pyx:894:12: 'H5PY_OBJ' is not a constant, variable or function identifier
      Loading library to get build settings and version: libhdf5.dylib
      ,********************************************************************************
                             Summary of the h5py configuration

      HDF5 include dirs: []
      HDF5 library dirs: []
           HDF5 Version: (1, 14, 2)
            MPI Enabled: False
       ROS3 VFD Enabled: False
       Rebuild Required: True

      ,********************************************************************************
      Executing api_gen rebuild of defs
      Executing cythonize()
      [ 1/24] Cythonizing /private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-install-8b6c2mrb/h5py_3a9bffda4ab548d5ac5aea13ae9c6ee1/h5py/_conv.pyx
      Traceback (most recent call last):
        File "/Users/foo/.venv/testing-h5py/lib/python3.8/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 353, in <module>
          main()
        File "/Users/foo/.venv/testing-h5py/lib/python3.8/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 335, in main
          json_out['return_val'] = hook(**hook_input['kwargs'])
        File "/Users/foo/.venv/testing-h5py/lib/python3.8/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py", line 251, in build_wheel
          return _build_backend().build_wheel(wheel_directory, config_settings,
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/build_meta.py", line 434, in build_wheel
          return self._build_with_temp_dir(
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/build_meta.py", line 419, in _build_with_temp_dir
          self.run_setup()
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/build_meta.py", line 341, in run_setup
          exec(code, locals())
        File "<string>", line 104, in <module>
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/__init__.py", line 103, in setup
          return distutils.core.setup(**attrs)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/_distutils/core.py", line 185, in setup
          return run_commands(dist)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/_distutils/core.py", line 201, in run_commands
          dist.run_commands()
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/_distutils/dist.py", line 969, in run_commands
          self.run_command(cmd)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/dist.py", line 989, in run_command
          super().run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/_distutils/dist.py", line 988, in run_command
          cmd_obj.run()
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/wheel/bdist_wheel.py", line 364, in run
          self.run_command("build")
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/_distutils/cmd.py", line 318, in run_command
          self.distribution.run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/dist.py", line 989, in run_command
          super().run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/_distutils/dist.py", line 988, in run_command
          cmd_obj.run()
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/_distutils/command/build.py", line 131, in run
          self.run_command(cmd_name)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/_distutils/cmd.py", line 318, in run_command
          self.distribution.run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/dist.py", line 989, in run_command
          super().run_command(command)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/setuptools/_distutils/dist.py", line 988, in run_command
          cmd_obj.run()
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-install-8b6c2mrb/h5py_3a9bffda4ab548d5ac5aea13ae9c6ee1/setup_build.py", line 170, in run
          self.extensions = cythonize(self._make_extensions(config),
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/Cython/Build/Dependencies.py", line 1154, in cythonize
          cythonize_one(*args)
        File "/private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-build-env-uvpwfguv/overlay/lib/python3.8/site-packages/Cython/Build/Dependencies.py", line 1321, in cythonize_one
          raise CompileError(None, pyx_file)
      Cython.Compiler.Errors.CompileError: /private/var/folders/2f/1mkpnp3n1gjd0r7l9nm_dyhr0000gn/T/pip-install-8b6c2mrb/h5py_3a9bffda4ab548d5ac5aea13ae9c6ee1/h5py/_conv.pyx
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for h5py
Failed to build h5py
ERROR: Could not build wheels for h5py, which is required to install pyproject.toml-based projects
WARNING: There was an error checking the latest version of pip.
```

幾つかの`Cython`のバージョン(3.0.4, 0.29.14, 0.29.13, 0.29, 0.28)を用いて、`h5py-3.6.0`をソースコードのtarballからのビルドを試みましたが、ビルドできるバージョンを確認できませんでした。

ただし回避策はいくつかあります。1つ目は最新の`h5py`をインストールする方法です。現時点(2023-10-21)での最新の`h5py`のバージョンは`3.10.0`です。そこで`Evolution Gym`の`requirements.txt`の`h5py==3.6.0`の部分を`h5py==3.10.0`にして、インストールを行います。筆者の環境では`Cython-3.0.4`をインストールした状態で`h5py==3.10.0`をソースコードからインストールできる事を確認できました。

2つ目は`h5py`をインストールしないという方法です。`Evolution Gym`のコードをgrepした所、`h5py`は`examples`ディレクトリ配下のサブモジュールのソースコードで使われていました。`examples`ディレクトリは`Evolution Gym`を用いた実験の実装例を示すものであり、`Evolution Gym`本体ではありません。そこで`Evolution Gym`の`requirements.txt`の`h5py==3.6.0`の部分を削除して、インストールを行います。この状態のインストールで`Evolution Gym`の機能の全てが適切に使用できるとは言えませんが、`Evolution Gym`のシミュレータを起動できる事を確認しました。

この問題については、これら2つの回避方法を使って`Evolution Gym`のインストール作業を進める事ができます。

### 画面がないことによる失敗(例えばDockerコンテナなど)

`Docker`を用いて`Evolution Gym`を実行する場合、インストールはうまくいくものの、シミュレータの起動に失敗することがあります。

*動作確認用のスクリプトの実行でシミュレータの起動に失敗する場合の出力:*
```
$ python example/gym_test.py
Using Evolution Gym Simulator v2.2.5
Error initializing GLFW.
```

これは`GLFW`が使用できない環境でシミュレータを起動しようとするために発生します。例えば`CUI`しかない`Docker`のコンテナ内や`GNU/Linux`環境では、当然シミュレータを起動することができません。その場合、仮想画面を使用する必要があります。

*仮想画面を使用して動作確認用のスクリプトを実行する:*
```
xvfb-run python example/gym_test.py
```
しかし、この場合実際の画面は表示されず、画像としてファイルに出力されるため、通常とは挙動が異なることになります。可能なら`GUI`で実行する環境を整えて実施することをおすすめします。どうしてもコンテナ内で実行させたい場合はX転送を使う方法もあるとは思いますが、未検証です。

### シミュレータ起動時に`SEGFAULT`してしまう

この失敗の原因はいまのところわかりません。ビルドした共有オブジェクトを一度削除し、再度`Evolution Gym`をインストールしてみるとうまくいく可能性があります。

## 原因究明の方法

失敗の原因を調べるのに正しい方法はありません。ただし、こんなふうにやると何かわかるかもしない程度の参考として記載しておくことにします。共通するのは、エラーメッセージをよく見て、そのエラーの特定をしていることだけです。

インストール時のエラーでは、以下の出力をよく見てみましょう。

*インストール失敗時によく表示される出力:*
```
        File "/usr/local/Cellar/python@3.8/3.8.17_1/Frameworks/Python.framework/Versions/3.8/lib/python3.8/subprocess.py", line 364, in check_call
          raise CalledProcessError(retcode, cmd)
      subprocess.CalledProcessError: Command '['cmake', '--build', '.', '--config', 'Release', '--', '-j8']' returned non-zero exit status 2.
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for evogym
Failed to build evogym
ERROR: Could not build wheels for evogym, which is required to install pyproject.toml-based projects
```

`Evolution Gym`はインストール時にシミュレータをビルドするために、`setup.py`の中でサブプロセスとしてビルドコマンドを実行しています。この部分は正にそれを表しています。

```
subprocess.CalledProcessError: Command '['cmake', '--build', '.', '--config', 'Release', '--', '-j8']' returned non-zero exit status 2.
```

このコマンドの後ろが実際に実行されているコマンドで、サブプロセスの起動時に文字列のリストで、コマンドと引数を指定しています。よく見るとわかりますが、これはただの`cmake`コマンドであって、当然ターミナルエミュレータで手入力することもできます。手動で実行する場合は次のようになります。

*`cmake`を手動で実行する場合のコマンド:*
```
cmake --build . --config Release -- -j8
```

この方法では内部で実行されている処理を分解することができるので、あたりをつけてこのようにして掘り下げていくことにより、原因を特定しやすくなります。
