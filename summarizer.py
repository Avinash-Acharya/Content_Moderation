import time
import torch
from transformers import AutoTokenizer, BartForConditionalGeneration

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
fb = "sshleifer/distilbart-cnn-12-6"
model = BartForConditionalGeneration.from_pretrained(fb)
tokenizer = AutoTokenizer.from_pretrained(fb)
model.to(device)

def summarize(allPara):
    """
    Summarizes the given text using a pre-trained model.
    Args:
        allPara (str): The input text to be summarized.
    Returns:
        str: The summarized text.
    Description:
        This function takes a long paragraph of text and generates a summary using a pre-trained model. 
        It tokenizes the input text, determines the appropriate summary length, and then generates the summary. 
        The function also prints the time taken to generate the summary.
    """

    start = time.time()
    inputs = tokenizer(allPara,max_length=1024, truncation=True, padding="longest", return_tensors="pt")
    input_length = inputs['input_ids'].shape[1]
    max_summary_length = min(int(input_length * 0.3), 400)
    min_summary_length = max(int(input_length * 0.1), 100)
    summary_ids = model.generate(inputs["input_ids"], min_length=min_summary_length, max_length=max_summary_length)
    result = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    end = time.time()
    time_taken = end - start
    print(f"Time taken to summarize: {time_taken:.2f} seconds")
    return result