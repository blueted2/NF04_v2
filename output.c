typedef struct { 
  int var_entier;
  float var_reel;
  int tab_entier[12];
} nv_type;

void main() { 
  int (*truc)[12];
  int tab2[20];

  truc = test2(tab2, 20);
}