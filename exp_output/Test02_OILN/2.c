int main(int argc, char *argv[])
{
  int i;
  int n;
  int temp;
  int sum = 0;
  int flag = 10;
  scanf("%d\n", &n);
  for (i = 0; i < n; i++)
  {
    scanf("%d", &temp);
    sum += temp;
  }

  if ((sum > 10) && ((sum + flag) < 20))
  {
    sum -= 10;
    if (flag > 10)
    {
      sum++;
    }
    else
      if (flag < 10)
    {
      sum--;
    }
    else
    {
      sum = sum * 2;
    }


  }

  if (sum > 20)
  {
    if ((sum > 30) && (sum < 40))
    {
      sum -= 10;
    }

  }

  printf("%d\n", sum);
}

