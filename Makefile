FILES= seg.py vision.py requirements.txt README
ARCHIVE = rcal_regourd_sokolov.tar.gz

.PHONY: all clean

all: $(ARCHIVE)

$(ARCHIVE): $(FILES)
	tar -czvf $@ $^

clean:
	${RM} ${RMFLAGS} $(ARCHIVE)
