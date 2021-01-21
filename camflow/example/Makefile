example:
	test -f venv/bin/activate || virtualenv -p Python2.7 venv
	. venv/bin/activate ; \
		pip install xxhash tqdm ; \
		python ../prepare.py -i trace_attack6.data -o processed_attack6.txt -t -O path_attack6.txt -p ; \
		python ../parse.py -i processed_attack6.txt -b 4000 -B base_attack6.txt -S stream_attack6.txt -t

stats:
	test -f venv/bin/activate || virtualenv -p $(shell which python) venv
	. venv/bin/activate ; \
		pip install xxhash tqdm ; \
		python ../prepare.py -s -v -i data.txt -o preprocessed.txt ; \
		python ../parse.py -i preprocessed.txt -B base.txt -S stream.txt -s -I 10

clean:
	rm -rf preprocessed.txt debug.log stats.csv base.txt stream.txt ts.txt
	rm -rf venv
