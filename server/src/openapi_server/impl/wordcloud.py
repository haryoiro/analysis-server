from openapi_server.data_models.models import Opinion, RepresentativeOpinion, TalkSession, TalkSessionReport
import pandas as pd
import numpy as np
import json
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sqlalchemy import select
from wordcloud import WordCloud
import io
import os
from datetime import datetime
import base64

from openai import OpenAI
api_key = os.getenv('OPEN_AI_API_KEY', '')
client = None
if api_key != '':
    client = OpenAI(api_key=api_key)

TOP_N = 3
Session = None

SYSTEM_TEMPLATE ="あなたは文のリストから共通している部分を見つけ出す優秀なアナリストです。あなたは、文のリストの全てに共通していることをまとめた要約文を作成することです。"
HUMAN_TEMPLATE ="""# 命令
以下の文のリストの全てに共通していることをまとめた要約文を作成してください。異なる文のリストを与えられたときに、異なる要約文となるように、固有で独自のものになるよう注意してください。

# 制約条件
- 要約文は5文字以上30文字以下でなければならない
- 要約文は文のリストの全てに共通していることを表していなければならない
- 要約文は簡潔で分かりやすい言葉を使うこと
- 異なる文のリストを与えられたときに、異なる要約文となるように、固有で独自の要約文でなければならない

# 文のリスト
{texts}
"""

def get_embedding(text, model='text-embedding-ada-002'):
    response = client.embeddings.create(
        input=text,
        model=model,
    )
    prompt_tokns = response.usage.prompt_tokens
    price = prompt_tokns * 0.0001 / 1000
    return response.data[0].embedding, price

def get_summary(text_list):
    functions = [
        {
            "name": "make_summary",
            "description": "文のリストから共通していることをまとめた要約文を作成する",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "文のリストから共通していることをまとめた要約文"
                    }
                },
                "required": ["summary"]
            }
        }
    ]
    texts = "\n".join(text_list)
    messages = [
        {"role": "system", "content": SYSTEM_TEMPLATE},
        {"role": "user", "content": HUMAN_TEMPLATE.format(texts=texts)},
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        functions=functions,
        function_call={"name": "make_summary"},
        temperature=0.9,
    )

    # responseのtoken数を取得
    prompt_tokns = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens

    # priceを計算
    price = (prompt_tokns * 0.001 / 1000) + (completion_tokens * 0.002 / 1000)

    response_item = response.choices[0].message
    try:
        function_args = json.loads(response_item.function_call.arguments)
        summary_text = function_args["summary"].strip()
        return summary_text, price
    except:
        return "", price

def prepare_dataset(session, talk_session_id: str):
    Session = session
    texts = []
    with Session() as session:
        stmt = select(Opinion).where(Opinion.talk_session_id == talk_session_id)
        result = session.execute(stmt).all()
        for row in result:
            texts.append(row.Opinion.content)

    text_df = pd.DataFrame([], columns=['text', 'embedding', 'price'])
    total_price = 0
    embedding_list = []

    for text in texts:
        embedding, price = get_embedding(text)
        text_df.loc[len(text_df)] = {'text': text, 'embedding': embedding, 'price': price}
        total_price += price
        embedding_list.append(embedding)

    matrix = np.vstack(text_df['embedding'].values)
    n_clusters = 10

    kmeans = KMeans(n_clusters = n_clusters, init='k-means++', random_state=0)
    kmeans.fit(matrix)
    text_df['label'] = kmeans.labels_

    df = text_df.copy()
    text_list_by_cluster = [text_df[text_df['label'] == i]['text'].tolist() for i in range(n_clusters)]

    cluster_df = pd.DataFrame([], columns=['text', 'count', 'label', 'price'])
    total_price = 0

    for label, text_list in enumerate(text_list_by_cluster):
        summary_text, price = get_summary(text_list)
        cluster_df.loc[len(cluster_df)] = {
            "text": summary_text,
            "count": len(text_list),
            "label": label,
            "price": price
        }
        total_price += price

    wordcloud = WordCloud(width=800, height=400, background_color='white',
                         font_path='./SourceHanSerifK-Light.otf')
    wordcloud.generate_from_frequencies({row.text: row.count for row in cluster_df.itertuples()})
    wordcloud_buffer = io.BytesIO()
    wordcloud.to_image().save(wordcloud_buffer, format='png')


    label_df = cluster_df.copy()
    label_df = label_df.sort_values('count', ascending=False)
    top_labels = []
    label_dict = {}
    label_color_dict = {}
    # 上位20個までの色を用意
    total_color_list = [
        "purple", "green", "red", "blue", "yellow", "orange", "pink", "brown", "gray", "black", "gold", "cyan", "lime",
        "silver", "maroon", "olive", "teal", "navy", "fuchsia", "crimson"]
    color_list = []
    idx = 0
    for _, row in label_df.head(TOP_N).iterrows():
        top_labels.append(int(row['label']))
        label_dict[int(row['label'])] = row['text']
        label_color_dict[total_color_list[idx]] = int(row['label'])
        color_list.append(total_color_list[idx])
        idx += 1

    df = df[df['label'].isin(top_labels)]
    # dfからembeddingのみを抽出
    df = df[['embedding', 'label']]
    # dfからembeddingのリストを作成
    embeddings = df['embedding'].tolist()
    # dfのレコード数を確認
    matrix = np.vstack(embeddings)

    n_samples = matrix.shape[0]
    perplexity = min(15, n_samples - 1)  # 15かn_samples - 1の小さい方を選択
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=0, init="random", learning_rate=200)
    vis_dims2 = tsne.fit_transform(matrix)

    x = [x for x, y in vis_dims2]
    y = [y for x, y in vis_dims2]

    # labelのリストを作成
    labels = df['label'].tolist()
    # labelをstrからintに変換
    labels = [int(label) for label in labels]

    plt.figure()
    for category, color in enumerate(color_list):
        indices = [i for i, label in enumerate(labels) if label == label_color_dict[color]]
        xs = np.array(x)[indices]
        ys = np.array(y)[indices]
        plt.scatter(xs, ys, color=color, alpha=0.3)

        avg_x = xs.mean()
        avg_y = ys.mean()

        plt.scatter(avg_x, avg_y, marker="x", color=color, s=100, label=label_dict[label_color_dict[color]])

    plt.legend(loc='upper center', bbox_to_anchor=(.5, -.15))
    tsne_buffer = io.BytesIO()
    plt.savefig(tsne_buffer, format='png', bbox_inches='tight')
    plt.close()

    return wordcloud_buffer, tsne_buffer

def wordclouds(session, reports_generates_post_request):
    talk_session_id = reports_generates_post_request.talk_session_id
    wordcloud_bytes, tsne_bytes = prepare_dataset(session, talk_session_id)

    return {
        "wordcloud": base64.b64encode(wordcloud_bytes.getvalue()).decode('utf-8'),
        "tsne": base64.b64encode(tsne_bytes.getvalue()).decode('utf-8')
    }
