# Создаём индексы из файлов с описанием

echo "Creating index film: "
curl -X PUT http://elastic:9200/film -H 'Content-Type: application/json' --data-binary "@/elasticdump/film_idx.json"
echo ""

echo "Creating index genre: "
curl -X PUT http://elastic:9200/genre -H 'Content-Type: application/json' --data-binary "@/elasticdump/genre_idx.json"
echo ""

echo "Creating index person: "
curl -X PUT http://elastic:9200/person -H 'Content-Type: application/json' --data-binary "@/elasticdump/person_idx.json"
echo ""

sleep 1

# Грузим данные из дампов в индексы

echo ""
echo "Loading index film: "
/usr/local/bin/elasticdump --input=/elasticdump/film_dump.json --output=http://elastic:9200/film
echo ""

echo "Loading index genre: "
/usr/local/bin/elasticdump --input=/elasticdump/genre_dump.json --output=http://elastic:9200/genre
echo ""

echo "Loading index person: "
/usr/local/bin/elasticdump --input=/elasticdump/person_dump.json --output=http://elastic:9200/person
echo ""
