# Replication Package README

This is the replication package for the paper: "Understanding Code Snippets in Code Reviews: A Preliminary Study of the OpenStack Community", including dataset and so on (see the description below).

## File Organization

- **Data of Code Snippets in Code Review.xlsx** is the dataset of our paper, which contains 10,790 review comments collected from the Nova project and Neutron project of OpenStack community. Among all the review comments, 626 review comments contain code snippets. For the rows of review comments with code snippets, we filled them with blue color as an indicator.
- **Examples for Each Purpose.xlsx** contains six review comment examples for the six detailed purposes mentioned in our paper (see Section 4.2).
- **README.md** 



## How To Read Dataset

The dataset excel file contains 2 sheets for Nova and Neutron respectively.  Each sheet has 13 columns for 13 data items. We listed them with descriptions and sources in a table below. 

| Data Item |                         Description                          |  Source  |
| :-------: | :----------------------------------------------------------: | :------: |
|  Author   | The author of the message as an [AccountInfo](https://review.opendev.org/Documentation/rest-api-accounts.html#account-info) entity. |  Gerrit  |
| Change_id | The code change id of the review comment, which consists of community, project, branch  and commit information, which could be used to locate the code change. |  Gerrit  |
|  Updated  |       The timestamp of when this comment was written.        |  Gerrit  |
| Patch_set | The specific patchset number of the review comment within the code change. |  Gerrit  |
|   Line    | The line number in the file at which the review comment is added. |  Gerrit  |
|   File    | The related file of the review comment within the code change. |  Gerrit  |
|  Message  |                     The comment message.                     |  Gerrit  |
|   Label   | Whether the review comment contains the code snippets (i.e., Yes or No). | Manually |
| Reviewer  | Whether the review comment is provided by reviewer (i.e., Yes or No). | Manually |
|  Purpose  | The high-level purpose behind the code snippets provided by reviewer. | Manually |
|  Detail   | The detailed purpose behind the code snippets provided by reviewer. | Manually |
| Accepted  | Whether the developer accepted the code snippets with suggestion purpose (i.e., Yes or No). | Manually |
| Evidence  | The url which could be used to prove the code snippets were accepted by the developer. | Manually |


# 复现包说明

这是论文《理解代码评审中的代码片段：对 OpenStack 社区的初步研究》的复现包，包含数据集等文件。

## 文件组成

- **Data of Code Snippets in Code Review\.xlsx**：论文使用的数据集，包含从 OpenStack 社区的 Nova 和 Neutron 项目收集的 10,790 条评审评论。其中 626 条评论包含代码片段；这些评论所在的行以蓝色标记。
- **Examples for Each Purpose.xlsx**：论文第 4.2 节所述六种具体目的各自对应的评审评论示例。
- **README.md**：数据集说明文件。

## 如何阅读数据集

数据集 Excel 文件包含两张工作表，分别对应 Nova 和 Neutron。每张表有 13 列：

| 数据项         | 含义                                      | 来源     |
| ----------- | --------------------------------------- | ------ |
| `Author`    | 评论作者，以 Gerrit 的 AccountInfo 账户信息形式表示。   | Gerrit |
| `Change_id` | 评论对应的代码变更 ID，包含社区、项目、分支和提交信息，可用于定位代码变更。 | Gerrit |
| `Updated`   | 评论撰写时的时间戳。                              | Gerrit |
| `Patch_set` | 该评论在代码变更中对应的补丁集编号。                      | Gerrit |
| `Line`      | 添加评论时所对应的文件行号。                          | Gerrit |
| `File`      | 评论所关联的文件。                               | Gerrit |
| `Message`   | 评论内容。                                   | Gerrit |
| `Label`     | 评论是否包含代码片段，取值为 Yes 或 No。                | 人工标注   |
| `Reviewer`  | 评论是否由评审者提供，取值为 Yes 或 No。                | 人工标注   |
| `Purpose`   | 评审者提供代码片段的总体目的。                         | 人工标注   |
| `Detail`    | 评审者提供代码片段的具体目的。                         | 人工标注   |
| `Accepted`  | 开发者是否接受了以提出建议为目的的代码片段，取值为 Yes 或 No。     | 人工标注   |
| `Evidence`  | 可用于证明开发者接受代码片段的链接。                      | 人工标注   |
