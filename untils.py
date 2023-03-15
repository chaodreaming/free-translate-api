import glob
import json
import os.path
import jieba
from sacremoses import MosesDetokenizer, MosesPunctNormalizer, MosesTokenizer
from subword_nmt import apply_bpe
import  tensorflow as tf
import numpy as np
if tf.__version__ >= '2.0':
    tf = tf.compat.v1
    tf.disable_eager_execution()

class supertranslate():
    def __init__(self, model_dir):
        self.model_dir=model_dir
        self.config=os.path.join(self.model_dir,"configuration.json")
        with open(self.config) as f:
            self.config_data=json.load(f)

        self.src_lang=self.config_data["preprocessor"]["src_lang"]
        self.src_bpe_path=os.path.join(self.model_dir,self.config_data["preprocessor"]["src_bpe"]["file"])
        self.src_vocab_path=os.path.join(self.model_dir,self.config_data["dataset"]["src_vocab"]["file"])
        self.trg_vocab_path=os.path.join(self.model_dir,self.config_data["dataset"]["trg_vocab"]["file"])

        self.src_vocab_size=self.config_data[ "model"]["src_vocab_size"]
        self.trg_vocab_size = self.config_data["model"]["trg_vocab_size"]
        self.pb_path=os.path.join(self.model_dir,os.path.basename(self.model_dir)+".pb")
        print(self.pb_path)

        self.trans_sess=self.model_init()
    def convert_characters(self,src_str):

        char_dict={'𝑎': 'a', '𝑏': 'b', '𝑐': 'c', '𝑑': 'd', '𝑒': 'e', '𝑓': 'f', '𝑔': 'g', '𝑖': 'i', '𝑗': 'j', '𝑘': 'k', '𝑙': 'l', '𝑚': 'm', '𝑛': 'n', '𝑜': 'o', '𝑝': 'p', '𝑞': 'q', '𝑟': 'r', '𝑠': 's', '𝑡': 't', '𝑢': 'u', '𝑣': 'v', '𝑤': 'w', '𝑥': 'x', '𝑦': 'y', 'ℎ': 'h'}
        # print(char_dict)
        for char, letter in char_dict.items():
            src_str = src_str.replace(char, letter)
        return  src_str
    def preprocess(self,input_sequence:list):
        # detokenizer
        # detok = MosesDetokenizer(lang=src_lang)

        # byte-pair-encoding
        bpe = apply_bpe.BPE(open(self.src_bpe_path))

        if self.src_lang == 'zh':
            tok = jieba
            input_tok = [tok.cut(item) for item in input_sequence]
            input_tok = [' '.join(list(item)) for item in input_tok]
        else:
            punct_normalizer = MosesPunctNormalizer(lang=self.src_lang)
            tok = MosesTokenizer(lang=self.src_lang)
            input_sequence = [punct_normalizer.normalize(item) for item in input_sequence]
            input_tok = [tok.tokenize(
                item, return_str=True, aggressive_dash_splits=True) for item in input_sequence]

        input_bpe = [bpe.process_line(item).strip().split() for item in input_tok]

        src_vocab = dict([
            (w.strip(), i) for i, w in enumerate(open(self.src_vocab_path))
        ])
        MAX_LENGTH = max([len(item) for item in input_bpe])
        input_ids = np.array([[
                                  src_vocab[w]
                                  if w in src_vocab else self.src_vocab_size
                                  for w in item
                              ] + [0] * (MAX_LENGTH - len(item)) for item in input_bpe])
        result = {'input_ids': input_ids}
        # print(result)
        # 对的结果 {'input_ids': array([[9036,  942,   25, 2502,    9,    6,  725,    1,  188,   37,  120,
        #          827,  297]])}
        return result
    def postprocess(self,outputs):
        # outputs = {'output_seqs': trans_ids}
        x, y, z = outputs['output_seqs'].shape
        translation_out = []
        for i in range(x):
            output_seqs = outputs['output_seqs'][i]
            wids = list(output_seqs[0]) + [0]  # 词表中位置0对应的token是句子结束符 </s>
            wids = wids[:wids.index(0)]

            trg_rvocab = dict([
                (i, w.strip()) for i, w in enumerate(open(self.trg_vocab_path))
            ])
            translation = ' '.join([
                trg_rvocab[wid] if wid in trg_rvocab else '<unk>'
                for wid in wids]).replace('@@ ', '').replace('@@', '')
            detok = MosesDetokenizer(lang=self.src_lang)
            translation_out.append(str(detok.detokenize(translation.split())).replace("\"", ""))

        result = {"translation": translation_out}
        # print(result)
        return result
    def model_init(self):
        print("Initializing")
        tf_config = tf.ConfigProto(allow_soft_placement=True)
        tf_config.gpu_options.allow_growth = True
        _session = tf.Session(config=tf_config)
        with _session.as_default() as sess:
            sess.run(tf.tables_initializer())

            graph = tf.Graph()
            with tf.gfile.GFile(self.pb_path, "rb") as f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(f.read())

            with graph.as_default():
                tf.import_graph_def(graph_def, name='')
            graph.finalize()
        trans_sess = tf.Session(graph=graph)
        input_dict = self.preprocess(["a"])
        trans_sess.run("NmtModel/strided_slice_9:0",
                                        feed_dict={"input_wids:0": input_dict['input_ids']})

        print("Initialization completed")
        return trans_sess
    def translate(self,input_sequence:list):

        input_dict = self.preprocess(input_sequence)
        trans_ids = self.trans_sess.run("NmtModel/strided_slice_9:0",
                                        feed_dict={"input_wids:0": input_dict['input_ids']})
        return self.postprocess({"output_seqs": trans_ids})


