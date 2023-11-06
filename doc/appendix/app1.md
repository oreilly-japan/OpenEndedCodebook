---
title: 付録1 NEAT-Pythonの使い方の理解を深める
date: 2023-07-15T18:14:38+0900
lastmod: 2023-07-15T18:14:38+0900
---


# 付録1 NEAT-Pythonの使い方の理解を深める

本書ではNEAT-Pythonをベースに各種アルゴリズムの実装を行っています。そのため、全体的にNEAT-Pythonの知識があることが前提となっています。2章ではNEAT-Pythonの使い方について説明しましたが、より理解を深めていただけるように、さらにサンプルを用意しました。2章の論理回路の例から少し難易度を上げ、より実例に近いクッキー探しゲームを作ってみます。端末上にお菓子のクッキー🍪を表示し、エージェント😃が画面上を探し回ります。ライブラリには標準ライブラリとNEAT-Pythonを使います。まずゲームを実装する前に、少しだけ `curses` のおさらいをしましょう。 `curses` は端末制御ライブラリで、端末上の表示を操作できます。

(注意 :: Windows用のPyhtonには `curses` がインストールされていません。その場合には、Dockerなどを用いて実行すると良いでしょう。)

```python
import curses

stdscr = curses.initscr()                # 画面を初期化する
stdscr.addch(0, 0, "😃")                 # 1文字表示する
stdscr.addstr(0, 2, " < Hello, world!")  # 文字列を表示する
stdscr.refresh()                         # 画面の変更を反映する
stdscr.getch()                           # 入力を待ち受ける
curses.endwin()                          # cursesを終了する
```

これは端末上に「😃 < Hello, world!」を表示します。これらの機能を使い、クッキー🍪やエージェント😃を表示します。エージェントはNEATによって徐々に賢くなっていきます。

まず、NEAT-Python用の設定ファイルを作成します。

```ini
[NEAT]
fitness_criterion     = max
fitness_threshold     = 100
pop_size              = 10
reset_on_extinction   = False
no_fitness_termination= False

[DefaultGenome]
# network parameters
num_inputs              = 3
num_hidden              = 1
num_outputs             = 2
feed_forward            = True
initial_connection      = partial_direct 0.5

# node activation options
activation_default      = sigmoid
activation_mutate_rate  = 0.0
activation_options      = sigmoid

# node aggregation options
aggregation_default     = sum
aggregation_mutate_rate = 0.0
aggregation_options     = sum

# connection add/remove rates
conn_add_prob           = 0.5
conn_delete_prob        = 0.5

# node add/remove rates
node_add_prob           = 0.2
node_delete_prob        = 0.2

# connection enable options
enabled_default         = True
enabled_mutate_rate     = 0.01

# node bias options
bias_init_mean          = 0.0
bias_init_stdev         = 1.0
bias_max_value          = 30.0
bias_min_value          = -30.0
bias_mutate_power       = 0.5
bias_mutate_rate        = 0.7
bias_replace_rate       = 0.1

# node response options
response_init_mean      = 1.0
response_init_stdev     = 0.0
response_max_value      = 30.0
response_min_value      = -30.0
response_mutate_power   = 0.0
response_mutate_rate    = 0.0
response_replace_rate   = 0.0

# connection weight options
weight_init_mean        = 0.0
weight_init_stdev       = 1.0
weight_max_value        = 30
weight_min_value        = -30
weight_mutate_power     = 0.5
weight_mutate_rate      = 0.8
weight_replace_rate     = 0.1

# genome compatibility options
compatibility_disjoint_coefficient = 1.0
compatibility_weight_coefficient   = 0.5

[DefaultSpeciesSet]
compatibility_threshold = 3.3

[DefaultStagnation]
species_fitness_func = max
max_stagnation       = 100
species_elitism      = 1

[DefaultReproduction]
elitism            = 2
survival_threshold = 0.1
min_species_size   = 2
```

次に、NEATアルゴリズムを実行するための、設定の読み込みや母集団を管理するクラスのインスタンス化を行います。


```python
from neat.config import Config
from neat.genes import DefaultNodeGene
from neat.genome import DefaultGenome
from neat.population import Population
from neat.reproduction import DefaultReproduction
from neat.species import DefaultSpeciesSet
from neat.stagnation import DefaultStagnation

c = Config(
    DefaultGenome,
    DefaultReproduction,
    DefaultSpeciesSet,
    DefaultStagnation,
    "simple.conf",
)
p = Population(c)
```

評価関数は、扱う問題によって異なるので、実装します。

```python
from neat.nn import FeedForwardNetwork

def eval_genomes(genomes, config, foo):
    for genome_id, genome in genomes:
        net = FeedForwardNetwork.create(genome, config)  # ニューラルネットワークの構築
        # === ドメインに依存する処理を実装する ===
        input_data = [0, 0, 0]  # 入力ノードに渡す値
        output_data = net.activate(input_data)  # 出力ノードから値を受け取る
        genome.fitness = 1  # 適応度を設定
        # === ドメインに依存する処理ここまで ===
```

「ドメインに依存する処理を実装する」というコメントの箇所に各個体の評価を実装し、その個体の成績を適応度として `genome.fitness` に設定します。この「ドメインに依存する処理」が今回はクッキー探しゲームとなります。ゲームを組み込んだ、評価関数 `eval_genomes` を改めて実装し直します。

```python
import curses
import itertools
import math
import time

from neat.nn import FeedForwardNetwork

def eval_genomes(genomes, config, foo):
    for genome_id, genome in genomes:
        net = FeedForwardNetwork.create(genome, config)

        # ================ ドメインに依存する処理を実装する ==========
        genome.fitness = 0
        BLANK = " "
        GOAL = "🍪"
        AGENT = "😃"  # エージェントの生成
        GAME_CLEAR = "😍"
        GAME_OVER = "👽"

        goal = [10, 10]  # ゴール (この場所を探す)
        current = [30, 80]  # エージェントの開始位置

        stdscr = curses.initscr()  # 画面の初期化
        stdscr.addch(goal[0], goal[1], GOAL)  # ゴール

        for i in itertools.count():
            # 表示を更新
            stdscr.addstr(0, 0, f"GENOME: {genome.key} | life: {i} | current: {current} | fitness: {genome.fitness}                        ")
            if goal == current:  # ゴールに到達
                genome.fitness += 1000  # 報酬を追加

                stdscr.addstr(0, 0, f"GENOME: {genome.key} | life: {i} | current: {current} | fitness: {genome.fitness}                        ")
                stdscr.addch(current[0], current[1], GAME_CLEAR)
                stdscr.refresh()
                time.sleep(5)
                break

            if i > 100:  # 寿命に到達
                # ゴールと自分自身の距離を測る
                distance = math.sqrt(
                    (goal[0] - current[0]) ** 2 + (goal[1] - current[1]) ** 2
                )
                genome.fitness -= distance  # 報酬を追加

                # ゲームオーバー
                try:
                    stdscr.addstr(0, 0, f"GENOME: {genome.key} | life: {i} | current: {current} | fitness: {genome.fitness}                        ")
                    stdscr.addch(current[0], current[1], GAME_OVER)
                    stdscr.refresh()
                    time.sleep(0.3)
                    stdscr.addch(current[0], current[1], BLANK)
                except curses.error:  # 画面はみ出し（文字だけ表示）
                    stdscr.addstr(1, 1, f"DEAD")
                    stdscr.refresh()
                    time.sleep(0.3)
                    stdscr.addstr(1, 1, f"    ")
                    stdscr.refresh()
                break

            try:
                # エージェント描画
                stdscr.addch(current[0], current[1], AGENT)
                stdscr.refresh()
                time.sleep(0.01)
                stdscr.addch(current[0], current[1], BLANK)
            except curses.error:
                pass  # 画面はみ出し（無視する）

            # 移動
            input_data = [
                i,
                current[0],  # 現在位置
                current[1],  # 現在位置
            ]
            o_xy = net.activate(input_data)
            axis = 0 if o_xy[0] > o_xy[1] else 1
            amount = 1 if o_xy[axis] < 0.5 else -1

            stdscr.refresh()
            if (current[axis] + amount) > 1:
                current[axis] += amount
        # ================ ドメインに依存する処理ここまで ===========
```

この評価関数を `Population` クラスのインスタンスの `run()` メソッドに渡し、アルゴリズムを開始します。

```python
winner = p.run(eval_genomes, n=100)  # 10世代
curses.endwin()  # ゲーム画面の終了
print(winner)
```

実行すると、エージェントがクッキーを探して動き回ります。クッキーに辿り着くか、ゲームオーバーになると、エージェントは停止します。これを指定した世代まで繰り返し実行し、最も成績の良い個体を返します。
