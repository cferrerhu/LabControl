function [outVec] = hamming(N, a0)
%UNTITLED6 Summary of this function goes here
%   Detailed explanation goes here

x = 1:N;
outVec = a0-(1-a0).*cos((2*pi/N).*x);

end

