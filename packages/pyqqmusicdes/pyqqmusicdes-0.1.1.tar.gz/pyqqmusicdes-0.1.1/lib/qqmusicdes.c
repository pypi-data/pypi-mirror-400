#include "qqmusicdes.h"
#include "des.h"

int qq_music_triple_des_decrypt(unsigned char* buff, unsigned char* key, int len) {
	BYTE schedule[3][16][6];
	three_des_key_setup(key, schedule, DES_DECRYPT);
	for (int i = 0; i < len; i += 8)
		three_des_crypt(buff + i, buff + i, schedule);
	return 0;
}
