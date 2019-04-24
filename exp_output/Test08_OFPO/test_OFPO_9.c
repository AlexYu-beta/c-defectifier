char flag = 'N';
static int test = 20;
int func(int a, char b)
{
  if ((a % 2) == 0)
    return a;
  else
    if (b == 'b')
    return a * 2;
  else
    return a * 3;


}

void func2(int a, int b)
{
  printf("%d\n", a + b);
}

void func3(int a, char b, int c, char d, int e)
{
  printf("hello world");
}

int main(int argc, char *argv[])
{
  int i;
  int j;
  int n;
  int temp;
  int sum = 0;
  scanf("%d\n", &n);
  for (i = 0; i < n; i++)
  {
    scanf("%d", &temp);
    sum += temp;
  }

  for (j = 0; j < n; j++)
    func2(j, j + 1);

  switch (flag)
  {
    case 'N':
      func2(sum, 1);

    case 'Y':
      sum--;
      break;

    default:
      func2(sum + 1, sum);

  }

  if (func(sum, 'b') > test)
  {
    if ((sum > 30) && (sum < 40))
    {
      func2(sum, 1);
    }

    if (sum == 100)
      goto a_label;

  }

  int h = 0;
  func3(1, 'e', h, 'f', 10);
  do
  {
    printf("%d\n", h);
  }
  while (h < 0);
  printf("%d\n", sum);
  a_label:
  printf("%d\n", sum);

}

