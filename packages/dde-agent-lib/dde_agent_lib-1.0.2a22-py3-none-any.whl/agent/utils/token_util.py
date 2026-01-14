import tiktoken,os

os.environ["TIKTOKEN_CACHE_DIR"] = "/tmp/token_cache"
encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

def count_tokens(text):
    return len(encoding.encode(text))


if __name__ == "__main__":
    token_count = count_tokens("今天天气不错")
    print(token_count)
