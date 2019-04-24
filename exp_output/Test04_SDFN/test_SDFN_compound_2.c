char flag = 'N';
static int test = 20;
int func(int a)
{
  if ((a % 2) == 0)
    return a;
  else
    return a * 2;

}

void func2(int a)
{
  printf("%d\n", a + 1);
}

int main(int argc, char *argv[])
{
  int i;
  int j;
  int n;
  int temp;
  int sum = 0;
  for (i = 0; i < n; i++)
  {
    scanf("%d", &temp);
    sum += temp;
  }

  for (j = 0; i < n; j++)
    func2(j);

  switch (flag)
  {
    case 'N':
      func2(sum);

    case 'Y':
      sum--;
      break;

    default:
      func2(sum);

  }

  if (func(sum) > test)
  {
    if ((sum > 30) && (sum < 40))
    {
      func2(sum);
    }

    if (sum == 100)
      goto a_label;

  }

  int h = 0;
  do
  {
    printf("%d\n", h);
  }
  while (h < 0);
  printf("%d\n", sum);
  a_label:
  printf("%d\n", sum);

}

