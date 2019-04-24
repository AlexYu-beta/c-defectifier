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
  scanf("%d\n", &n);
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

  a_label:
  printf("%d\n", sum);

  printf("%d\n", sum);
  do
  {
    printf("%d\n", h);
  }
  while (h < 0);
}

