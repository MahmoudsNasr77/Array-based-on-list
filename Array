 public class List{
 public static void main(String[] args) {
    Scanner s =new Scanner (System.in);
   ArrayList a1=new ArrayList(10);
   a1.Insert(0, 10);
   a1.Insert(1, 20);
   a1.Insert(2, 10);
   a1.updateElement(6, 2);

      
   
  
   a1.Display();
    


}
}

class ArrayList{
    int[] Arr;
    int max,len;
    
    
    public ArrayList(int size) {
        if (size<0){
            System.out.println("Enter Postive Element");
            System.exit(0);
        }
        else {
            max=size;
        }
        len=0;
        Arr=new int [max];  
    }
    public boolean isEmpty(){
        return len==0;
    }
    public boolean isFull(){
        return len==max;
    }
    public int getSize(){
    return len;
    }
    public void Display(){
        System.out.print("[");
        for (int i=0;i<len;i++){
            System.out.print(Arr[i]+" ");
        }
        System.out.print("]");
    }
    public void Insert(int pos,int element){
        if (isFull()){
            System.out.println("List is Overflow");
        }
        else if (pos<0){
            System.out.println("Out Of Range");
        }
        else {
        for (int i=len;i>pos;i--){
            Arr[i]=Arr[i-1];
        }
        Arr[pos]=element;
        len++;
    }
    }
    
    public void Remove(int pos){
      if (isEmpty()){
          System.out.println("List is Underflow");
      }  else if (pos<0||pos>len){
          System.out.println("Out Of Range");
      }else {
          for (int i=pos;i<len;i++){
              Arr[i]=Arr[i+1];
              
          }
          len--;
      }
    }
    public boolean Serach(int element){
        if(isEmpty()){
            System.out.println("Array is Underflow");
        }
        else 
            for (int i=0;i<len;i++){
                if (Arr[i]==element){
                    return true;
                }
                else 
                    return false;
            }
            return false;
    }
    public void insertAtEnd(int element){
        if (isFull()){
            System.out.println("Array is Overflwo");
        }
        else
            Arr[len]=element;
        len++;
    }
    public void updateElement(int elemnt,int pos){
        if (pos<0)
            System.out.println("Array out of Range"); 
        else 
            Arr[pos]=elemnt;
        
    }
    
    
}
}
