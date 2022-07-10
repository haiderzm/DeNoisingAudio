import pydub
import streamlit as st
import tensorflow as tf
import numpy as np

from io import BytesIO


from main import model

batching_size = 12000


def handle_uploaded_audio_file(uploaded_file):
    st.write("Type : ", type(uploaded_file))

    a = pydub.AudioSegment.from_wav(uploaded_file)
    # a = uploaded_file.read()

    # st.audio(a)

    st.write("A : ", type(a))

    # st.write("Width : ",a.sample_width)

    samples = a.get_array_of_samples()
    # st.write(type(samples))
    # st.write(samples.typecode)
    # st.write(type(samples.type))
    # st.write(samples)
    # samples = np.frombuffer(a,dtype=np.float32)
    fp_arr = np.array(samples).T.astype(np.float32)
    fp_arr /= np.iinfo(samples.typecode).max
    # st.write(fp_arr)
    # fp_arr = samples
    fp_arr = fp_arr.reshape(fp_arr.shape[0],1)
    # samples = samples.reshape(samples.shape[0],1)
    # fp_arr = tf.convert_to_tensor(samples, dtype=tf.float32)
    fp_arr = tf.convert_to_tensor(fp_arr, dtype=tf.float32)
    # st.write(type(fp_arr))
    # st.write(fp_arr.shape)


    # samples = np.frombuffer(a,dtype=np.float32)
    # load_bytes = BytesIO(a)
    # fp_arr = samples
    # fp_arr = fp_arr / np.iinfo('h').max
    # st.write(fp_arr)
    # fp_arr = fp_arr.reshape(fp_arr.shape[0],1)
    # fp_arr = tf.convert_to_tensor(fp_arr, dtype=tf.float32)

    # st.audio(samples)
    st.write(a)




    return fp_arr


def audio_to_display(audio):
    audio_file = open(audio, 'rb')
    audio_bytes = audio_file.read()
    return audio_bytes


def get_audio(path):
    audio, _ = tf.audio.decode_wav(tf.io.read_file(path), 1)
    # st.write(type(audio))
    
    # st.write("Tf Shape : ", audio.shape)
    return audio


def inference_preprocess(uploaded_file):
    # audio = get_audio(path)
    audio = handle_uploaded_audio_file(uploaded_file)
    audio_len = audio.shape[0]
    batches = []
    for i in range(0, audio_len - batching_size, batching_size):
        batches.append(audio[i:i + batching_size])

    batches.append(audio[-batching_size:])
    diff = audio_len - (i + batching_size)
    return tf.stack(batches), diff


def predict(uploaded_file):
    test_data, diff = inference_preprocess(uploaded_file)
    predictions = model.predict(test_data)
    final_op = tf.reshape(predictions[:-1], ((predictions.shape[0] - 1) * predictions.shape[1], 1))
    final_op = tf.concat((final_op, predictions[-1][-diff:]), axis=0)
    return final_op
