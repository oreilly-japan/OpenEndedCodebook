---
title: 付録5 Evolution Gymのタスク
date: 2023-07-15T18:14:38+0900
lastmod: 2023-07-15T18:14:38+0900
---

# 付録5 Evolution Gymのタスク

本書のサンプルプログラムでは、32個のタスクを用意しています。これらはEvolution Gymのサイトで用意されているタスクと同じものです。多様なロボットがさまざまなタスクを解こうとします。

## ウォーキングタスク
### Walker-v0
ロボットは平坦な地形の上をできるだけ遠くまで歩きます。ロボットが正のX方向に移動すると報酬が与えられます。1回の実行で500ステップ実行されます。また、端に辿り着くと1回限りの報酬として1を受け取ります。

![Walker-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.8より引用) )][image-45]

### BridgeWalker-v0
ロボットは柔らかい橋の上をできるだけ遠くまで歩きます。ロボットが正のX方向に移動すると報酬が与えられます。1回の実行で500ステップ実行されます。また、端に辿り着くと1回限りの報酬として1を受け取ります。

![BriedgeWalker-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.9より引用) )][image-46]

### BidirectionalWalker-v0
ロボットは双方向に歩きます。またタスク中にゴールの位置xがランダムに変化します。ゴールが何回変化したかをカウントされ（カウンタ c ）、x方向のゴールに向かって移動すると報酬が与えられます。1回の実行で1,000ステップ実行されます。
![BidirectionalWalker-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.10より引用) )][image-47]

## 物体操作タスク
### Carrier-v0
ロボットは箱をできるだけ遠くに運びます。報酬はロボットと箱を正のx方向にどれだけ移動させたかの合計で与えられます。箱を落とすとペナルティが与えられます。1回の実行で500ステップ実行され、端に辿り着くと1回限りの報酬として1を受け取ります。
![Carrier-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.11より引用) )][image-48]

### Carrier-v1
ロボットは箱を運び、地形の終端付近に置いてあるテーブルの上に箱を置きます。箱をx方向にテーブルまで移動したら報酬を与え、落としたらペナルティを与えます。1回の実行で1,000ステップ実行されます。
![Carrier-v1 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.12より引用) )][image-49]

### Pusher-v0
ロボットは手前に置かれた箱を押します。ロボットと箱が正のx方向に動けば報酬を与え、x方向から離れればペナルティを与えます。1回の実行で500ステップ実行され、端に辿り着くと1回限りの報酬として1を受け取ります。
![Pusher-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.13より引用) )][image-50]

### Pusher-v1
ロボットの後ろに置かれた箱を、ロボットが前進方向に押したり引いたりします。ロボットと箱が正のx方向に動けば報酬を与え、x方向から離れればペナルティを与えます。1回の実行で600ステップ実行され、端に辿り着くと1回限りの報酬として1を受け取ります。
![Pusher-v1 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.14より引用) )][image-51]

### Thrower-v0
ロボットが箱を投げます。箱が正のx方向に動けば報酬を与え、箱を投げるときにx = 0から離れすぎるとペナルティが与えられます。1回の実行で300ステップ実行されます。
![Thrower-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.15より引用) )][image-52]

### Catcher-v0
ロボットは高速で回転する箱をキャッチし運びます。ロボットがx方向に箱を移動したら報酬を与え、箱を落としたらペナルティを与えます。1回の実行で400ステップ実行されます。物体の落ちてくる位置が毎回異なるため、難易度が実行ごとに異なります。このタスクを実行するときは `eval-num` オプションを2回以上に設定することが適当です。
![Catcher-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.16より引用) )][image-53]

### BeamToppler-v0
ロボットは2本の棒の上に乗っているブロックを間から押し上げて下に落とします。x方向にブロックの位置までへの移動、ブロックの移動、そしてブロックを下に落とすことに対して報酬が与えられます。1回の実行で1,000ステップ実行され、タスクを完了すると1回限りの報酬として1が与えられます。
![BeamToppler-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.17より引用) )][image-54]

### BeamSlider-v0
ロボットは、間隔を開けてブロックを並ぶ棒を下から滑らせます。ロボットがブロックをx方向に移動すると報酬が与えられます。1回の実行で1,000ステップ実行されます。
![BeamSlider-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.18より引用) )][image-55]

### Lifter-v0
ロボットは穴から箱を持ち上げます。ロボットが箱を正のy方向に移動させると報酬を与え、箱を落とすとペナルティが与えられます。1回の実行で300ステップ実行されます。
![Lifter-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.19より引用) )][image-56]

## クライミングタスク
### Climber-v0
ロボットは、上に伸びる平らな管を垂直にできるだけ高く登ります。ロボットが正のy方向に移動すると報酬が与えられます。1回の実行で400ステップ実行され、タスクを完了すると1回限りの報酬として1が与えられます。
![Climber-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.20より引用) )][image-57]

### Climber-v1
ロボットは、剛体とソフトな素材が混在した上に伸びる管を垂直にできるだけ高く登ります。ロボットが正のy方向に移動すると報酬が与えられます。1回の実行で600ステップ実行され、タスクを完了すると1回限りの報酬として1が与えられます。
![Climber-v1 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.21より引用) )][image-58]

### Climber-v2
ロボットは、階段状の管をできるだけ高く登ります。ロボットは正のx方向かy方向に移動すると報酬が与えられます。1回の実行で1,000ステップ実行されます。
![Climber-v2 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.22より引用) )][image-59]

## 前方移動タスク
### UpStepper-v0
ロボットはさまざまな長さの階段を登っていき、正のX方向に移動すると報酬が与えられます。また、地形の端に到達すると1回限りの報酬として2が与えられ、元の方向からどちらかの方向に75度以上回転すると-3のペナルティがあります（その後、環境はリセットされます）。1回の実行で600ステップ実行されます。
![UpStepper-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.23より引用) )][image-60]

### DownStepper-v0
ロボットはさまざまな長さの階段を降りていき、正のX方向に移動すると報酬が与えられます。また、地形の端に到達すると1回限りの報酬として2が与えられ、元の方向からどちらかの方向に90度以上回転すると-3のペナルティがあります（その後、環境はリセットされます）。1回の実行で500ステップ実行されます。
![DownStepper-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.24より引用) )][image-61]

### ObstacleTraverser-v0
ロボットはだんだん凸凹になっていく地形を横切って歩きます。また、地形の端に到達すると1回限りの報酬として2が与えられ、元の方向からどちらかの方向に90度以上回転すると-3のペナルティがあります（その後、環境はリセットされます）。1回の実行で1,000ステップ実行されます。
![ObstacleTraverser-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.25より引用) )][image-62]

### ObstacleTraverser-v1
ロボットは非常に凸凹した地形の中を歩きます。 また、地形の端に到達すると1回限りの報酬として2が与えられます（その後、環境はリセットされます）。1回の実行で1,000ステップ実行されます。
![ObstacleTraverser-v1 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.26より引用) )][image-63]

### Hurdler-v0
ロボットは背の高い障害物がある地形を横切って歩きます。ロボットが正のX方向に移動すると報酬が与えられます。また、元の方向からどちらかの方向に90度以上回転すると-3のペナルティがあります（その後、環境はリセットされます）。1回の実行で1,000ステップ実行されます。
![Hurdler-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.27より引用) )][image-64]

### PlatformJumper-v0
ロボットは間隔を開けて配置された浮遊する高さの異なるバーを横切り、正のX方向に移動すると報酬が与えられます。また、ロボットが元の方向から90度以上回転したり、プラットフォームから落ちたりすると、一度だけ-3のペナルティを受けます（その後、環境はリセットされます）。1回の実行で1,000ステップ実行されます。
![PlatformJumper-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.28より引用) )][image-65]

### GapJumper-v0
ロボットは間隔を開けて配置されたすべて同じ高さで浮遊するバーを横切ります。ロボットが正のX方向に移動すると報酬が与えられます。また、プラットフォームから落ちると一度だけ-3のペナルティを受ける（その後、環境はリセットされます）。1回の実行で1,000ステップ実行されます。
![GapJumper-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.29より引用) )][image-66]

### Traverser-v0
ロボットは、硬いブロックがいくつも入っている穴を沈むことなく反対側へ横切ります。ロボットが正のX方向に移動すると報酬が与えられます。また、地形の端に到達すると1回限りの報酬として2を受け取ります（その後、環境はリセットされます）。1回の実行で1,000ステップ実行されます。
![Traverser-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.30より引用) )][image-67]

### CaveCrawler-v0
ロボットは、洞窟の中を障害物を避けながら通過し、正のx方向に移動すると報酬を与えます。また、地形の端に到達すると1回だけ報酬を受け取ります（その後、環境はリセットされます）。1回の実行で1,000ステップ実行されます。
![CaveCrawler-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.31より引用) )][image-68]

## 形状変化タスク
### AreaMaximizer-v0
このタスクでは、ロボットが可能な限り大きな表面積を占めるように成長し、成長すると報酬が与えられます。1回の実行で600ステップ実行されます。
![AreaMaximizer-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.32より引用) )][image-69]

### AreaMinimizer-v0
このタスクでは、ロボットは可能な限り小さな表面積を占めるように縮小し、縮むと報酬が与えられます。1回の実行で600ステップ実行されます。
![AreaMinimizer-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.33より引用) )][image-70]

### WingspanMaximizer-v0
このタスクでは、ロボットは可能な限り幅が広くなるように成長します。X方向に成長すると、ロボットに報酬が与えられます。1回の実行で600ステップ実行されます。
このタスクを指定するときは、 `-t WingspanMa**z**imizer-v0` と指定してください。
![WingspanMaximizer-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.34より引用) )][image-71]

### HeightMaximizer-v0
このタスクでは、ロボットは可能な限り背が高くなるように成長し、Y方向に成長すると報酬が与えられます。1回の実行で500ステップ実行されます。
![HeightMaximizer-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.35より引用) )][image-72]

## その他
### Flipper-v0
このタスクでは、ロボットは平坦な地形で、できるだけ多く反時計回りに回転します。反時計回りに回転することで報酬が得られます。1回の実行で600ステップ実行されます。
![Flipper-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.36より引用) )][image-73]

### Jumper-v0
このタスクでは、ロボットは平坦な地形でできるだけ高くその場でジャンプします。正のY方向に動くと報酬が与えられ、X方向に動くとペナルティが与えられます。1回の実行で500ステップ実行されます。
![Jumper-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.37より引用) )][image-74]

### Balancer-v0
このタスクでは、ロボットは細いポールの上でバランスをとります。x、y方向にバランスを取るように移動すると、報酬が与えられます。1回の実行で600ステップ実行されます。
![Balancer-v0 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.38より引用) )][image-75]

### Balancer-v1
このタスクでは、ロボットは細いポールの横からスタートしポールに飛び乗り、その上でバランスをとります。x、y方向にバランスを取るように移動すると報酬が与えられます。1回の実行で600ステップ実行されます。
![Balancer-v1 (Bhatia et al, Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots, In proc. of NeurIPS 2021, pp. 2201--2214, 2021 (Fig.39より引用) )][image-76]


[image-45]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Walker-v0.png?raw=true
[image-46]:	https://github.com/ryokoakaike/EC_image/blob/master/img/BridgeWalker-v0.png?raw=true
[image-47]:	https://github.com/ryokoakaike/EC_image/blob/master/img/BidirectionalWalker-v0%20.png?raw=true
[image-48]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Carrier-v0.png?raw=true
[image-49]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Carrier-v1.png?raw=true
[image-50]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Pusher-v0.png?raw=true
[image-51]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Pusher-v1.png?raw=true
[image-52]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Thrower-v0.png?raw=true
[image-53]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Catcher-v0.png?raw=true
[image-54]:	https://github.com/ryokoakaike/EC_image/blob/master/img/BeamToppler-v0.png?raw=true
[image-55]:	https://github.com/ryokoakaike/EC_image/blob/master/img/BeamSlider-v0.png?raw=true
[image-56]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Lifter-v0.png?raw=true
[image-57]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Climber-v0.png?raw=true#vertical
[image-58]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Climber-v1.png?raw=true#vertical
[image-59]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Climber-v2.png?raw=true#vertical
[image-60]:	https://github.com/ryokoakaike/EC_image/blob/master/img/UpStepper-v0.png?raw=true
[image-61]:	https://github.com/ryokoakaike/EC_image/blob/master/img/DownStepper-v0.png?raw=true
[image-62]:	https://github.com/ryokoakaike/EC_image/blob/master/img/ObstacleTraverser-v0.png?raw=true
[image-63]:	https://github.com/ryokoakaike/EC_image/blob/master/img/ObstacleTraverser-v1.png?raw=true
[image-64]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Hurdler-v0.png?raw=true
[image-65]:	https://github.com/ryokoakaike/EC_image/blob/master/img/PlatformJumper-v0.png?raw=true
[image-66]:	https://github.com/ryokoakaike/EC_image/blob/master/img/GapJumper-v0.png?raw=true
[image-67]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Traverser-v0.png?raw=true
[image-68]:	https://github.com/ryokoakaike/EC_image/blob/master/img/CaveCrawler-v0.png?raw=true
[image-69]:	https://github.com/ryokoakaike/EC_image/blob/master/img/AreaMaximizer-v0.png?raw=true
[image-70]:	https://github.com/ryokoakaike/EC_image/blob/master/img/AreaMinimizer-v0.png?raw=true
[image-71]:	https://github.com/ryokoakaike/EC_image/blob/master/img/WingspanMaximizer-v0.png?raw=true
[image-72]:	https://github.com/ryokoakaike/EC_image/blob/master/img/HeightMaximizer-v0.png?raw=true
[image-73]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Flipper-v0.png?raw=true
[image-74]:	https://github.com/ryokoakaike/EC_image/blob/master/img/%20Jumper-v0.png?raw=true
[image-75]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Balancer-v0.png?raw=true
[image-76]:	https://github.com/ryokoakaike/EC_image/blob/master/img/Balancer-v1.png?raw=true
