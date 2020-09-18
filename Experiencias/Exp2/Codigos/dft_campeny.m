function [dft_matrix] = dft_campeny(N)
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here
w = exp(-2*pi*1i/N);
dft_matrix = zeros(N,N);

for i=1:N
    for j=1:N
        dft_matrix(i,j) = w^(mod((i-1)*(j-1),N))./sqrt(N);
    end
end


end

