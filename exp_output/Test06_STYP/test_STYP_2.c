char flag = 'N';
static int test = 20;
int test2 = 3.4;
int func(int a)
{
  if ((a % 2) == 0)
    return a;
  else
    return a * 2;

}

int main(int argc, char *argv[])
{
  int i;
  int n;
  int temp;
  long sum = 0;
  scanf("%d\n", &n);
  for (i = 0; i < n; i++)
  {
    scanf("%d", &temp);
    sum += temp;
  }

  if (sum > 10)
  {
    sum -= test / 4;
    sum += (test + 1) + test;
  }

  if (func(sum) > test)
  {
    if ((sum > 30) && (sum < 40))
    {
      sum -= 10;
    }

  }

  printf("%d\n", sum);
}

