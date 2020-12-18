以下是本文第5章实例分析的实现流程介绍：

一. 程序部分
1. 数据抓取：由于抓取量大，时间跨度长，所以我们依托阿里云上的ubuntu操作系统服务器运行爬虫程序。文件夹“Spider on pc”和“Spider on ubuntu”分别是在pc端和服务器上的运行的程序代码，两者区别在于：前者的运行环境是python3.6后者是python3.5。（感谢李同学在爬虫编写上给予的指导帮助）
2. 词云制作：见“Word_cloud.ipynb”。
3. 数据预处理：见“Data_preprocessing.ipynb”。
4. 灰色关联分析通过DPS数据分析系统实现。
5. 时差相关分析通过R语言的ccf函数实现。
5. 贝叶斯优化算法选择超参数：见 “Bayesian_hyperparametric_optimization.ipynb”。
6. 预测模型：包括GM(1,1)、BPNN和XGBoost模型，其中GM(1,1)通过DPS数据分析系统构建，其余模型的实现代码见文件夹“Prediction model”。
7. COD综合舆情值和NH综合舆情值的计算：分别见“c_COD.ipynb”和“c_NH.ipynb”。
8. 画图：见“Graphs.ipynb”。

二. 数据部分
1. 农业源COD和氨氮排放量：见环保部发布的《中国生态环境统计年报》。
2. 其他数据：见文件夹“Data”。