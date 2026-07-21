library(rvest)
library(httr)
library(dplyr)
library(purrr)
library(tm)
library(tidytext)
library(wordcloud)
library(wordcloud2)
library(ggplot2)
library(RColorBrewer)
library(igraph)
library(ggraph)
library(tidyverse)
library(sentimentr)
library(syuzhet)

urls <- df$url

extract_text_from_url <- function(url) {
  tryCatch({
    page <- read_html(url)
    page %>% html_nodes("p") %>% html_text() %>% paste(collapse = " ")
  }, error = function(e) NA)
}

web_texts <- map(urls, extract_text_from_url)

results <- data.frame(url = urls, text = web_texts, stringsAsFactors = FALSE)

corpus <- Corpus(VectorSource(results$text))
corpus_clean <- corpus %>%
  tm_map(content_transformer(tolower)) %>%
  tm_map(removePunctuation) %>%
  tm_map(stripWhitespace) %>%
  tm_map(removeWords, stopwords("spanish"))

dtm <- DocumentTermMatrix(corpus_clean)
dtm_matrix <- as.matrix(dtm)
term_frequency <- sort(colSums(dtm_matrix), decreasing = TRUE)

term_df <- data.frame(term = names(term_frequency), freq = term_frequency)

ggplot(term_df[1:10, ], aes(x = reorder(term, freq), y = freq, fill = term)) +
  geom_bar(stat = "identity", show.legend = FALSE) +
  geom_text(aes(label = freq), hjust = -0.2, size = 3.5) +
  coord_flip() +
  theme_minimal()

set.seed(123)
wordcloud(words = names(term_frequency), freq = term_frequency, min.freq = 5,
          scale = c(3, 0.5), random.order = FALSE, colors = brewer.pal(8, "Dark2"))

wordcloud2(data = term_df, size = 1, shape = "square", backgroundColor = "white")

text_df <- data.frame(text = sapply(corpus_clean, as.character), stringsAsFactors = FALSE)

bigrams <- text_df %>%
  unnest_tokens(bigram, text, token = "ngrams", n = 2) %>%
  separate(bigram, into = c("word1", "word2"), sep = " ") %>%
  filter(!word1 %in% stopwords("spanish"), !word2 %in% stopwords("spanish"))

bigram_counts <- bigrams %>% count(word1, word2, sort = TRUE)

bigram_graph <- bigram_counts %>%
  filter(n > quantile(n, 0.95)) %>%
  graph_from_data_frame()

set.seed(123)
ggraph(bigram_graph, layout = "fr") +
  geom_edge_link(aes(edge_alpha = n), show.legend = FALSE) +
  geom_node_point(color = "gray", size = 3) +
  geom_node_text(aes(label = name), vjust = 1, hjust = 1) +
  theme_void()

web_texts_vector <- unlist(web_texts)
sentiment_scores <- sentiment(web_texts_vector)

sentiment_summary <- sentiment_scores %>%
  group_by(element_id) %>%
  summarize(
    avg_sentiment = mean(sentiment),
    positive_count = sum(sentiment > 0),
    neutral_count = sum(sentiment == 0),
    negative_count = sum(sentiment < 0)
  )

ggplot(sentiment_summary, aes(x = element_id, y = avg_sentiment)) +
  geom_bar(stat = "identity", fill = "steelblue") +
  theme_minimal()

ggplot(sentiment_scores, aes(x = sentiment)) +
  geom_density(fill = "lightblue", alpha = 0.7) +
  theme_minimal()

sentiment_classification <- sentiment_summary %>%
  gather(key = "sentiment_type", value = "count", positive_count:negative_count)

ggplot(sentiment_classification, aes(x = as.factor(element_id), y = count, fill = sentiment_type)) +
  geom_bar(stat = "identity", position = "dodge") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))

sentiment_scores2 <- get_sentiment(web_texts, method = "syuzhet")
emotion_scores <- get_nrc_sentiment(web_texts_vector)

bar_heights <- sort(colSums(prop.table(emotion_scores[, 1:8])))
par(mar = c(5, 10, 4, 2))
bar_positions <- barplot(bar_heights, horiz = TRUE, las = 1, col = rainbow(8), border = TRUE,
                         xlim = c(0, max(bar_heights) * 1.2))
text(x = bar_heights, y = bar_positions, labels = round(bar_heights, 3), pos = 4, cex = 0.8)

edges <- df_red

g <- graph_from_data_frame(edges, directed = TRUE)
plot(g)
