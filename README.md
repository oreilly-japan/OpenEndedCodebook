# 『Pythonではじめるオープンエンドな進化的アルゴリズム』サポートページ

<!--
```
brew install graphviz
conda create -n openevo python=3.8
conda activate openevo
conda install matplotlib==3.0.3
pip install -r requirements.txt
```

and install evogym.
https://evolutiongym.github.io/tutorials/getting-started.html
-->

## 環境とインストール方法

オープンエンドなアルゴリズムを実装済みのサンプルプログラムを用意しました。この
サンプルプログラムには、いくつかの実験を用意しています。それらを動作させながら、
アルゴリズムを学んでいただけます。ここではサンプルプログラムと、その実行環境のイ
ンストール方法を説明します。

### PythonとAnaconda

サンプルプログラムはPythonで実装されています。また本書で使用しているEvolution
Gym 1.0はPython 3.8をサポートしています。そのため本書でも、Python 3.8を使用しま
す。Python 3.8のインストール方法については割愛します。またAnacondaを使用します
が、Anacondaのインストール方法については割愛します。

 - Python：https://www.python.org/downloads/
 - Anaconda：https://docs.anaconda.com/

### Evolution Gym

サンプルプログラムではEvolution Gymを使います。Evolution Gymはシミュレーショ
ンの結果を表示するためにOpenGLを使用し、インストール時にシミュレータをビルドし
ます。ビルドには追加のライブラリが必要になります。

#### Windows

Windowsでは事前にGitとVisual Studioをインストールする必要があります。依存ラ
イブラリをインストールするには `winget` コマンドを用います。

```
$ winget install cmake
```

その後、`conda` コマンドでEvolution Gymをインストールします。

```
$ git clone --recurse-submodules https://github.com/EvolutionGym/evogym.git
$ cd evogym
$ conda env create -f environment.yml
```

#### GNU/Linux（例としてUbuntu）

GNU/Linuxの例としてUbuntuでの環境の構築方法を説明します。Ubuntuではaptコ
マンドを用いて依存ライブラリをインストールします。

```
$ apt install cmake glfw
```

その後、`conda` コマンドでEvolution Gymをインストールします。

```
$ git clone --recurse-submodules https://github.com/EvolutionGym/evogym.git
$ cd evogym
$ conda env create -f environment.yml
```

#### macOS

macOSの例としてHomebrewを使った環境の構築方法を説明します。

```
$ brew install cmake glfw
```

その後、 `conda` コマンドでEvolution Gymをインストールします。
```
$ git clone --recurse-submodules https://github.com/EvolutionGym/evogym.git
$ cd evogym
$ conda env create -f environment.yml
```

### サンプルプログラム

サンプルプログラムの実行環境を構築します。

1. サンプルプログラムのソースコードを取得する

   Github上にあるサンプルプログラムのソースコードを取得します。

   ```
   git clone https://github.com/oreilly-japan/OpenEndedCodebook.git
   ```

2. 作業ディレクトリをリポジトリルートに移動する

   ソースコードを取得できたら、作業ディレクトリをリポジトリルートに移動します。

   ```
   cd OpenEndedCodebook
   ```

3. 依存パッケージをインストールします。

   ```
   pip install -r requirements.txt
   ```

   本書で使用する依存パッケージの中に、以前のバージョンのライブラリを期待しているものがあります。ただしパッケージの状態により、依存パッケージの依存パッケージがインストールできない状態になっています。そのため `--no-deps` を指定してインストールします。

   ```
   pip install --no-deps -r requirements-extra.txt
   ```

これで環境構築は終わりです。

|*注意*：<br>Evolution Gymのインストールの際、プラットフォームによってはエラーが出ることがあります。その際は、こちらのURLをお使いください。<br>https://github.com/oreilly-japan/evogym|
|:-|
