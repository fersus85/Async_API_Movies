# Создаём индексы из файлов с описанием

echo "Creating index film: "
curl -X PUT http://elastic:9200/film -H 'Content-Type: application/json' --data-binary "@/test_dump/film_idx.json"
if [ $? -ne 0 ]; then
  echo "Failed to create index film"
  exit 1
fi

echo "Creating index genre: "
curl -X PUT http://elastic:9200/genre -H 'Content-Type: application/json' --data-binary "@/test_dump/genre_idx.json"
if [ $? -ne 0 ]; then
  echo "Failed to create index genre"
  exit 1
fi

echo "Creating index person: "
curl -X PUT http://elastic:9200/person -H 'Content-Type: application/json' --data-binary "@/test_dump/person_idx.json"
if [ $? -ne 0 ]; then
  echo "Failed to create index person"
  exit 1
fi

sleep 1

# Грузим данные из дампов в индексы

echo ""
echo "Loading index film: "
/usr/local/bin/elasticdump --input=/test_dump/test_film_dump.json --output=http://elastic:9200/film
if [ $? -ne 0 ]; then
  echo "Failed to load index film"
  exit 1
fi

echo "Loading index genre: "
/usr/local/bin/elasticdump --input=/test_dump/test_genre_dump.json --output=http://elastic:9200/genre
if [ $? -ne 0 ]; then
  echo "Failed to load index genre"
  exit 1
fi

echo "Loading index person: "
/usr/local/bin/elasticdump --input=/test_dump/test_person_dump.json --output=http://elastic:9200/person
if [ $? -ne 0 ]; then
  echo "Failed to load index person"
  exit 1
fi
